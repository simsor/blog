---
title: "Kindle Hacking: porting Doom to the Kindle 4"
date: 2021-01-07 21:00:00
draft: false
---

As promised, here is a writeup about how I [ported Doom to my old Kindle 4](https://twitter.com/simsor/status/1344702881065263105)! I will try to detail my thought process for each step, and why I chose to do it the way I did (spoiler: it's mostly because that's what worked first).

It could be useful to read [the previous part](https://sixfoisneuf.fr/posts/kindle-hacking-deeper-dive-internals/) if you haven't yet, because it details how the OS exposes the e-ink screen and hardware buttons to applications. Porting the game was mostly a matter of adapting the input and display code.

## Porting Doom, sure, but which one?

When the idea popped into my mind, I wasn't sure where to start. Obviously Doom had already been ported to [every](https://wiibrew.org/wiki/WiiDoom) [console](https://github.com/devinacker/prboom-3ds) (and a bunch of [non](https://www.youtube.com/watch?v=xZaKlLyikKg) [consoles](https://www.rockbox.org/wiki/PluginDoom)) under the sun. Before looking at any of these, I looked up the Doom source code, and it turns out it was simply available on GitHub at [`id-Software/DOOM`](https://github.com/id-Software/DOOM). Looking through the source code, it seemed that the graphical display was handled by the X11 library. Ugh. Also, it seemed like there was a bit of assembly in there for critical functions, and I did not feel like translating x86 assembly to armv7...

Looking at virtually every successful source port, I realised they were almost all based on [PrBoom](http://prboom.sourceforge.net/). I downloaded [DS DOOM](https://github.com/Doom-Utils/dsdoom) to have a look at what a port could look like...

I started by searching for "`<nds.h>`", [`libnds`](https://libnds.devkitpro.org/)'s header file. My reasoning was that files that needed special NDS handling would have to import this header.

```
$ fgrep -r '<nds.h>' arm9/ arm7
arm9/source/doomtype.h:#include <nds.h>
arm9/source/i_system.c:#include <nds.h>
arm9/source/i_video.c:#include <nds.h>
arm9/source/SDLnet.c:#include <nds.h>
arm9/source/SDLnetselect.c:#include <nds.h>
arm9/source/SDLnetsys.h:#include <nds.h>
arm9/source/SDLnetUDP.c:#include <nds.h>
arm9/source/SDL_net.h:#include <nds.h>
arm7/source/arm7_main.c:#include <nds.h>
```

Discarding the `SDL_` files, it looked like I would only have to edit a couple files:
- `i_video.c` -- Probably screen- and video-related functions
- `i_system.c` -- System-specific code? File management maybe?
- a `main` file

I had my mind set on PrBoom, so I [downloaded the latest version](https://sourceforge.net/projects/prboom/files/prboom%20stable/2.5.0/)! *(released in 2008, that's how you know something is **stable**)*

## Simplifying the build system

The first thing I saw when opening the source code was that it was using `autoconf` 😱 I don't really mind it when I'm only compiling something, but if I have to make changes to the code (especially deep changes like the ones I wanted to make), the simple thought of editing a `Makefile.in` makes me nauseous.

![](/images/prboom_autoconf.png)

I didn't care about my port being portable to other systems, so I promptly deleted all this stuff and started on an empty `Makefile`. A couple rules to build all C files in `src/`, another to link everything together and we were almost good to go! I also got rid of the `src/MAC` and `src/POSIX` folders, and renamed `src/SDL` to `KINDLE`.

Using `config.h`, I disabled most of everything that wasn't going to be essential in getting this thing running: OpenGL support, network support, high resolution support, etc. I also removed all `gl_*` files in `src/`. The goal was to reduce the scope as much as possible!

Finally, I had something that was almost working: the only issues were about nonexistent SDL functions being called. Time to translate them!

## How Doom handles the screen

In a stroke of genius (or good software craftsmanship), most of the Doom code never deals with the screen directly. Instead, the rendering engine works on virtual screens (6 by default), which are simply arrays of bytes. Once a frame, the main screen is copied to the physical screen by `I_FinishUpdate`. Similarly, the Doom engine never deals with raw keycodes directly: instead, they define all the keys they know about, and `I_GetEvent` will translate system-specific events into Doom events.

The SDL-specific code was enumerating possible screen sizes when intializing the screen, handled OpenGL and software rendering, stopped rendering when the program wasn't focused...I got rid of everything. My `I_FinishUpdate` function needed to do only one thing: copy `screens[0]` to the framebuffer while inverting all its pixels (the Kindle's screen displays `0x00` as a white pixel, and `0xFF` as black). No need for palette changes. No need for screen size adjustement.

The Kindle implementation goes from automatically determining the ideal screen resolution, color depth, etc. to hardcoding everything and calling `init_framebuffer()`:

```c
static int fbFd;

static void init_framebuffer() {
  fbFd = open("/dev/fb0", O_RDWR);
  if (fbFd == -1) {
    perror("open(/dev/fb0)");
    exit(1);
  }
}

void I_FinishUpdate (void)
{
    if (I_SkipFrame()) return;
    int h;
    byte *src;
    byte *dest;
  
    dest=screen;
    src=screens[0].data;
    h=SCREEN_HEIGHT;

    for (; h>0; h--)
    {
      memcpy(dest,src,SCREENWIDTH);
      for (byte* off=dest; off < dest+SCREENWIDTH; off++) {
        *off = ~*off; // Invert pixel color, 0xFF == black on the e-ink display
      }
      dest+=SCREEN_WIDTH;
      src+=screens[0].byte_pitch;
    }
    
    update_framebuffer(0);
}
```

*Side-note: hey, screens[4] is supposed to be the status bar...maybe I've been too harsh and that's why it keeps flickering?*

Similarly, `I_GetModeFromString` always returns `VID_MODE8`, because the Kindle display doesn't support anything else. We can then assume that all `screens` will have one byte per pixel and copy everything that way.

## Input handling

When it comes to input, the idea is pretty much the same: Doom translates key input in a single function and sends internal events to functions that need to react to these. By replacing `I_TranslateKey(SDL_Key*)` with our own code operating on Kindle keycodes, we were able to make the game react to button presses!

I first needed to open `/dev/input/event{0,1}` to react to all button presses on the Kindle:

```c
static int kindleKeysFd;
static int kindleKeysFd2;

typedef struct {
  int truc1;
	int truc2;
	unsigned short truc3;
  unsigned short keyCode;
  int status;
} kindle_key_t;

static void init_kindle_keys() {
  kindleKeysFd = open("/dev/input/event1", O_RDONLY|O_NONBLOCK);
  if (kindleKeysFd == -1) {
    perror("open(/dev/input/event1)");
    exit(1);
  }

  kindleKeysFd2 = open("/dev/input/event0", O_RDONLY|O_NONBLOCK);
  if (kindleKeysFd2 == -1) {
    perror("open(/dev/input/event0)");
    exit(1);
  }
}
```

I messed around with using `select(2)`, but I didn't find a reliable way to prevent it from blocking...so I went with the `O_NONBLOCK` solution, which seems a bit more hack-ish but works correctly.

Then, I changed `I_TranslateKey` to accept an `int` instead (the key code) and updated `I_GetEvent` to call `kindle_poll_keys` (I'm not gonna show this one because it's very ugly). Once translated, the key events are handled like normal by the Doom engine! Magic ✨

```c

static int I_TranslateKey(unsigned short code)
{
  int rc = 0;

  switch (code) {
    case KINDLE_LEFT: rc = KEYD_LEFTARROW; break;
    case KINDLE_RIGHT: rc = KEYD_RIGHTARROW; break;
    case KINDLE_UP: rc = KEYD_UPARROW; break;
    case KINDLE_DOWN: rc = KEYD_DOWNARROW; break;
    case KINDE_OK: rc = KEYD_RCTRL; break;
    default: break;
  }

  return rc;

}
```

That's it! Now everything should compile and I can go to bed!!

## Compilation woes

I'm going to try to retrace my steps as well as I can in this part, I tried a lot of things to fix my compilation problems:

- Using `musl`'s `libmath` implementation
- Compiling my own cross-compilation toolchain with `crosstool-NG` (ended up in a `Makefile` loop and almost crashed my machine)
- Compiling an old `glibc` version with my current toolchain
- Patching the ELF file to force it to use the correct `libc`

All these workaround were to fix the issue of the old as dirt `libc` on the Kindle: 2.12! Of course, my toolchain was compiled against `glibc` 2.31...and it's basically impossible to statically compile against `glibc`.

In the end, I used the `musl` toolchain from Bootlin and made `gcc` compile a static binary. I think fixing this version issue is what actually took me the longest time...

## `It works!`

Once this was done, and after understanding that I needed to also supply `prboom.wad` to PrBoom for it to work correctly, the game worked!!

![](/images/prboom_kindle.jpg)
![](/images/gzdoom_desktop.png)

*Small comparison of the graphical fidelity of the Kindle screen...*

I booted up in a non-working demo at first, which I fixed by using the `-warp` parameter to warp the player to E1M1. Rip and tear!!

## What's next?

I don't want to spend too much time on this project because it's never going to end up being playable due to the e-ink display. I still can't help but have ideas for the future:

- Fix the key handling code to allow binding a "Use" key, making the game theoretically playable from start to finish.
- Display the game in widescreen.
- Fix the demo playback and get rid of this "warp" hack.

Of course, if you're interested, I welcome all [pull requests](https://github.com/simsor/kindle-doom/) on the repository 😊