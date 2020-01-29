---
title: "Oculus Quest wireless casting"
date: 2020-01-29T18:48:00+001
draft: true
---

I recently caved in and acquired an [Oculus Quest](https://www.oculus.com/quest/). Even if Oculus is now part of the Facebook conglomerate (ugh), this piece of hardware is really impressive, and relatively affordable: you essentially get all the hardware you need to get access to the VR ecosystem for about ~€450. No need for a beefy PC or anything of the sort!

On the technical side, it seems the headset runs a modified Android version ([7.1.1 (Nougat)](https://en.wikipedia.org/wiki/Oculus_Quest) according to Wikipedia). It is relatively easy to enable developer mode and install unsigned APKs. The system supports running "flat" Android apps as well as VR games. [There's a whole ecosystem of custom apps!](https://sidequestvr.com/)

All interactions with the headset are supposed to go through the official Oculus app on your smartphone. Using the app, you can stream the view from inside the headset to your phone, tablet, or Chromecast-compatible receiver. Unfortunately, my TV doesn't have a built-in Chromecast 🙁

If you're in the same case, and would still appreciate to be able to cast your headset to your TV (VR is much more fun when there's an audience!), carry on reading!

## Technical solution

It's actually kinda easy: [Genymotion](https://www.genymotion.com/) (the people behind the Genymotion Android emulator) developed an Android screen sharing tool: [scrcpy](https://github.com/Genymobile/scrcpy). Turns out, it works pretty well on the Quest!

The steps are pretty simple:

- Get an ADB connection to your Quest
- Run the provided `scrcpy` executable

Provided you have `adb` on your system (it's included in the Windows release), it's only a matter of plugging your Quest to your computer and running:

```
$ adb list # Repeat until you see your Quest
$ ./scrcpy -c 1200:1000:130:250 -m 1024 -b 8M
```

With recent ADB versions, you can even use ADB over WiFi!

```
$ adb shell ip route
# Take note of your device ip
$ adb tcpip 5555
$ adb connect IP_ADDRESS

$ ./scrcpy -c 1200:1000:130:250 -m 1024 -b 8M
```