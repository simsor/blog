---
title: "Kindle hacking: a deeper dive into the internals"
date: 2021-01-01 22:12:00
draft: false
---

In this blog post, we will research in more details how the system interacts with all the different hardware components of this e-book reader. In the [previous blog post](https://sixfoisneuf.fr/posts/kindle-hacking-jailbreak/), we stayed within Amazon's "walled garden" (kind of): our apps had to use the Kindle Developement Kit, and with it all kinds of restrictions:

- No socket connection. All network connections **must** be HTTP/S.
- Cannot react to key presses however we want: for example, pressing Menu always brings up a menu.
- Cannot hide the status bar to create full-screen apps.

In addition, these apps have to be written with their old-ass Java subset and execute on their proprietary JVM. Surely we can do better!

## Executing native code

According to [Wikipedia](https://en.wikipedia.org/wiki/Amazon_Kindle), the Kindle 4 has a `Freescale i.MX508 800 MHz` processor. Running `uname` on the system confirms the exact architecture it is using:

```shell
$ uname -a
Linux kindle 2.6.31-rt11-lab126 #5 Sat Jan 12 20:39:09 PST 2013 armv7l unknown
```

Could it be as easy as compiling our code for an ARMv7 Linux target? Turns out, yes it is!

Let's try it out with a simple Go program:

```golang
package main

import "fmt"

func main() {
    fmt.Println("Hello, Kindle!")
}
```

Compiling it for a `linux/armv7` system is incredibly easy:

```shell
$ export GOOS=linux
$ export GOARCH=arm
$ export GOARM=7
$ go build
```

Let's try to run it on our Kindle!
```shell
$ ./kindle-test
Hello, Kindle!
```

It works!! But we are still limited to basic input-output from a SSH'd computer, which is not what we want! We now need a way to display stuff on the screen.

## Poking around the system

If you poke around the filesystem a little (or if you look on the [MobileRead Wiki](https://wiki.mobileread.com/wiki/Main_Page)), you will certainly find some interesting utilities:

- [`/usr/sbin/eips`](https://wiki.mobileread.com/wiki/Eips): write text or images to the screen, refresh it, clear it
- `/usr/bin/waitforkey`: waits for a key to be pressed or released on the Kindle and returns it, as well as its state.
- [`/usr/bin/lipc-*`](https://wiki.mobileread.com/wiki/Lipc): all kinds of utilities to use LIPC, an inter-process communication system specific to the Kindle series

Already, we get a way to draw arbitrary stuff to the screen and listen to key presses. That's promising! By shelling out to these programs in our apps, we can free ourselves from the constraints imposed by the Kindlet framework :)

The first version of [`go-kindle`](https://github.com/simsor/go-kindle) was only a simple wrapper around these three programs, and it was enough to develop some pretty nifty stuff! But shelling out isn't fun, so let's try to understand how they work!

## The e-ink framebuffer

In order to get a feel of what `eips` does, let's run it through `strace` to determine what it does when clearing the screen:

```shell
$ strace eips -c
...
open("/dev/fb0", O_RDWR)                = 3
ioctl(3, FBIOGET_VSCREENINFO, 0xbef7eae8) = 0
mmap2(NULL, 480000, PROT_READ|PROT_WRITE, MAP_SHARED|MAP_LOCKED, 3, 0) = 0x40127000
ioctl(3, FBIO_EINK_CLEAR_SCREEN, 0)     = 0
close(3)                                = 0
exit_group(0)                           = ?
+++ exited with 0 +++
```

`/dev/fb0`?! That's really interesting! This makes us think that the e-ink display is exposed through a semi-standard Linux Framebuffer device. "Semi-standard", because it uses both well-known ioctl codes such as [`FBIOGET_VSCREENINFO`](https://elixir.bootlin.com/linux/latest/ident/FBIOGET_VSCREENINFO) and seemingly unknown ones, like `FBIO_EINK_CLEAR_SCREEN`. *(Side note: does anyone know where `strace` is pulling these identifiers from?)*

Also, the `mmap`'d section is exactly 480000 bytes long, which is the result of `600 * 800`, the resolution of the display! Each byte must represent a pixel on the screen, with 255 possible color values.

Let's run strace again, but this time let's tell it not to pretty-print the identifiers: we want their real value!

```shell
$ strace -e ioctl -e raw=ioctl eips -c
ioctl(0x3, 0x4600, 0xbed19ae8)          = 0
ioctl(0x3, 0x46e1, 0)                   = 0
+++ exited with 0 +++
```

The first ioctl is `FBIOGET_VSCREENINFO`, but the second one is the one we were searching for: `FBIO_EINK_CLEAR_SCREEN`!

By using the same technique with the various [`eips` command switches](https://wiki.mobileread.com/wiki/Eips), we can find the following:

- `FBIO_EINK_CLEAR_SCREEN` = `0x46e1`
- `FBIO_EINK_UPDATE_DISPLAY` = `0x46db`
  - When passing the parameter `0` to this ioctl, the screen refreshes without blinking, but leaves "ghost" traces
  - When passing the parameter `1`, the screen does the well-known e-ink flash and cleanly redisplays its contents

We have now found a way to access the screen contents, change them, clear the screen and refresh it. That's perfect! This was the time when I updated `go-kindle` to directly access the framebuffer to display images! It still shells out to `eips` to display text because I still haven't gotten around to implementing that yet.

## Reading key presses

Let's use the same technique to have a look at `waitforkey`.

```shell
$ strace -e open,read waitforkey
open("/dev/input/event0", O_RDONLY)     = 3
open("/dev/input/event1", O_RDONLY)     = 4
open("/dev/input/event2", O_RDONLY)     = 5
open("/dev/input/event3", O_RDONLY)     = -1 ENOENT (No such file or directory)

# Here, I press "Down"

read(4, "\376\233\357_\354Y\16\0\1\0l\0\1\0\0\0", 16) = 16
108 1
+++ exited with 0 +++
```

The following happened:
- `waitforkey` opened three different input devices: `event0`, `event1` and `event2`
- `event1` produced something when I pressed the "Down" key

Here is the data that was read in hexdump form:
```shell
$ printf "\376\233\357_\354Y\16\0\1\0l\0\1\0\0\0" | hexdump -C
00000000  fe 9b ef 5f ec 59 0e 00  01 00 6c 00 01 00 00 00  |..._.Y....l.....|
00000010
```

The last four bytes look like a 4-byte integer reading `1`, which is the state that was returned. The four bytes before that read `01 00 6c 00`, which doesn't look like much...except if we remember we're also looking for `108`, or `0x6c`! The key code might then be only coded on two bytes.

I'm not sure what the other bytes mean yet, but we can create a struct to hold this information and read `/dev/input/event1` ourselves!

```c
typedef struct {
    unsigned int stuff1;
    unsigned int stuff2;
    unsigned short stuff3;
    unsigned short keyCode;
    unsigned int state;
} kindle_event_1_t
```

This allows us to react to the direction keys, as well as the "OK" key. Let's try to see what the other keys look like:

```shell
$ strace -e open,read waitforkey
open("/dev/input/event0", O_RDONLY)     = 3
open("/dev/input/event1", O_RDONLY)     = 4
open("/dev/input/event2", O_RDONLY)     = 5
open("/dev/input/event3", O_RDONLY)     = -1 ENOENT (No such file or directory)

# Press "Home"

read(3, "#\236\360_P\225\4\0\4\0\4\0\6\0\0\0", 16) = 16
read(3, "#\236\360_\335\225\4\0\1\0f\0\1\0\0\0", 16) = 16
102 1
+++ exited with 0 +++
```

This time, `waitforkey` read *twice* from `event0`. The data is as follows:

```shell
$ printf "#\236\360_P\225\4\0\4\0\4\0\6\0\0\0" | hexdump -C
00000000  23 9e f0 5f 50 95 04 00  04 00 04 00 06 00 00 00  |#.._P...........|
00000010
$ printf "#\236\360_\335\225\4\0\1\0f\0\1\0\0\0" | hexdump -C
00000000  23 9e f0 5f dd 95 04 00  01 00 66 00 01 00 00 00  |#.._......f.....|
00000010
```

The "Home" key is `102`, or `0x66`...there is a `0x66` in the second message, but not the first one. Let's try another button, "Back" (`0x9E`):

```
00000000  86 9f f0 5f 9c c1 0b 00  04 00 04 00 07 00 00 00  |..._............|
00000010

00000000  86 9f f0 5f 26 c2 0b 00  01 00 9e 00 01 00 00 00  |..._&...........|
00000010
```

The interesting bit is at the same place! I'm not sure what the first message is for, but we can re-use the first `struct` and add a define:

```c
#define KINDLE_KEY_BEGIN_MESSAGE 4
```

This way, after reading from `event0`, if the `keyCode` is `KINDLE_KEY_BEGIN_MESSAGE`, we know we need to read again to get the real data. I updated `go-kindle` to do this automatically!

## The inter-process communication system: `LIPC`

While looking for ways to get the SSID of the access point the Kindle was connected to, I stumbled upon the [MobileRead page on `lipc`](https://wiki.mobileread.com/wiki/Lipc). It looked like a proprietary inter-process communication system, and the list of endpoints was really interesting: we could get battery information, WiFi data, and a bunch of other stuff!!

Running `lipc-probe -a` gives us a list of *all* the processes connected to LIPC and what they're exposing:

```
com.lab126.pmond
	r 	Str	summary
	w	Str	start
	w	Str	restart
	w	Str	stop
	rw	Str	logMask
	w	Str	kill
	w	Str	heartbeat_start
	w	Str	mem_limit
	rw	Str	logLevel
	w	Str	heartbeat_stop
com.lab126.powerd
	w 	Int	addSuspendLevels
	r	Str	status
	w	Int	wakeUp
	rw	Int	preventScreenSaver
	rw	Str	logMask
	w	Int	suspendGrace
	w	Int	deferSuspend
	rw	Str	logLevel
	w	Int	touchScreenSaverTimeout
	r	Str	state
	w	Int	abortSuspend
	r	Int	isCharging
	r	Int	battLevel
	w	Int	rtcWakeup
com.lab126.system
	w 	Str	date
	r	Str	version
	r	Str	boardid
	r	Str	waveformversion
	r	Str	usid
	r	Str	orientation
	w	Str	sendEvent
com.lab126.wifid
	rw 	Has	createProfile
	r	Str	signalStrength
	rw	Has	cmNWProperties
	rw	Has	netConfig
	r	Str	manufacturerCode
	rw	Has	profileData
	w	Int	hotSpotDBDownloadStatus
	r	Str	feelingLuckyProfile
	w	Str	cmDisconnect
	rw	Has	currentEssid
	r	Str	711
	r	Int	profileCount
	w	Str	cmConnMode
	r	Str	cmState
	w	Str	scan
	rw	Str	logMask
	rw	Has	createNetConfig
	r	Int	scanListCount
	w	Str	cmCheckConnection
	r	Int	cmIntfInUse
	rw	Int	enable
	r	Str	macAddress
	rw	Str	logLevel
	w	Str	deleteProfile
	r	Str	scanState
	w	Str	cmConnect
	rw	Has	scanList
	rw	Has	cmIntfInfo
	r	Str	macSecret
com.lab126.framework
	rw 	Has	transfer_status
	w	Int	clearRffItems
	w	Int	insertKeystroke
	r	Str	xfsn
	rw	Str	logMask
	w	Int	logContent
	rw	Str	logLevel
	r	Int	wirelessSwitch
	w	Int	read
	r	Int	isRegistered
	r	Int	wanSwitch
	w	Int	dismissDialog
com.lab126.transfer
	rw 	Has	dump_queues
	rw	Has	modify
	rw	Has	get_info
	rw	Has	request_upload
	rw	Has	dequeue
	rw	Str	logMask
	rw	Str	logLevel
	rw	Has	send_status
	rw	Has	request_download
	rw	Has	obliterate
com.lab126.phd
	w 	Str	newSPHSchedule
	rw	Str	logMask
	rw	Str	logLevel
com.lab126.volumd
	r 	Int	mmcIsAvailable
	r	Int	userstoreFreeSpace
	r	Int	driveModeState
	r	Int	mmcFreeSpace
	rw	Int	useUsbForSerial
	w	Int	userstoreReadyToUnMount
	rw	Str	logMask
	r	Int	mmcTotalSpace
	rw	Int	useUsbForNetwork
	r	Int	userstoreTotalSpace
	rw	Str	logLevel
	r	Int	userstoreIsAvailable
com.lab126.webreaderListener
com.lab126.cmd
	r 	Str	activeInterface
	w	Str	ensureConnection
	rw	Str	logMask
	rw	Str	logLevel
	rw	Int	wirelessEnable
	rw	Has	availableInterfaces
	rw	Has	interfaceProperties
com.lab126.cvm
	rw 	Str	logMask
	rw	Str	logLevel
```

Wow wow wow 😍 There's everything we could ever want in there!! We can see three data types:
- `Int`: integer type
- `Str`: string type
- `Has`: hash array type (a map basically)

`r` means we can only read from it, `w` that we can only write to it, and I'll let you guess what `rw` means 😉

Reading and writing to basic types (`int` and `str`) can be done with `lipc-get-prop` and `lipc-set-prop`. Hash arrays must be read with `lipc-hash-prop -n` and written to with `lipc-hash-prop`. It only says "Accepts a Hasharray from the input stream", I don't know what format is expected.

Running `strace lipc-get-prop com.lab126.wifid 711` shows some interesting stuff, such as the process opening `/var/run/dbus/system_bus_socket`. This protocol might be written on top of dbus! I have dug any deeper on this yet, because shelling out to the various `lipc` binaries is less of a performance issue than for the other parts (I'm not checking the battery state 20 times a second).

## Conclusion

Wow, this took longer than expected! I wanted to talk about my [Doom port]() but I feel like it would make for too big of a post! This will have to wait for the next one 😛

Digging into the Kindle internals was really interesting, and also a great source of learning: I didn't know much about framebuffers or ioctls before jumping in. The next step will be to contribute back to the MobileRead wiki with everything I've found! Thanks a bunch to these people!!