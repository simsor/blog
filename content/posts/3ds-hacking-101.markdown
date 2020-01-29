---
title: "3DS Hacking 101 (WIP)"
date: 2017-01-23 21:52:19 +0100
draft: false
---

3DS hacking can be a bit daunting to approach even by tech-savvy people
because of the lingo and all the different security measures
implemented by Nintendo. This post will try to clear everything up.

Most of the information here comes from [3DBrew](http://3dbrew.org).

<!-- more -->

# Glossary

  - o3DS(XL): Original 3DS (the first model) and its XL counterpart
  - n3DS(XL): Upgraded 3DS (New 3DS & New 3DS XL)
  - 2DS: the 2DS if functionnaly the same as an o3DS, so it's just called "o3DS"
  - CTR: codename for the 3DS
  - NAND: Flash memory, the "hard disk" of your 3DS. Different from the SD Card!
  - ARM: A processor type, the brains of the console
  - CFW: Custom FirmWare, a 3DS firmware that's been modified to add features

# Processors

The 3DS (Old, New and 2D) has 3 different processors:

  - ARM11
  - ARM9
  - ARM7

The ARM11 processor is the one used during normal gameplay and in the
menus. When in 3DS mode, the ARM9 processor is used for all
security-related functions. It manages the access to NAND etc.  If the
ARM11 tries to do something, it has to gain permission from the ARM9
in most cases.

The ARM7 is used when playing DS or GBA games (through the Nintendo
Ambassador program).
	
# CIAs
	
CIA (CTR Importable Archive) is a file format which represents
basically any title on your 3DS, as well as system updates. Most CIAs
are digitally signed, which means they can only be installed on a
single 3DS (the one it's signed for).

When you attempt to install a CIA, the ARM11 processor signals the
ARM9 processor, and the ARM9 checks the signature of the file. If it's
invalid, it stops the ARM11 from installing the CIA. The signature is
also checked when the 3DS discovers the games that are installed on
the SD card: if a game's signature doesn't match the 3DS's, it isn't
shown on the Home screen.
		
There is a special case of CIA signature where the file is signed for
everyone, meaning the ARM9 always accepts the signature. These are
called "Legit CIA".
	
System updates are such legit CIAs. However, before applying a system
update, ARM9 checks for the version to be installed to prevent a
downgrade. In system versions <11.x, there was a bug which allowed us
to circumvent that check.

# Hacks (hax)

There are 3 big types of "hack" in the 3DS scene:

  - ARM11 userland access: allows running the Homebrew Launcher
  - ARM11 kernel access: allows installing legit CIAs
  - ARM9 exploits: allows almost full control over the 3DS, like installing unsigned CIAs
	
Most (if not all) hacks use the "hax" suffix, and you almost always
have to check the GitHub repository to know what type of hack you're
dealing with.

In order to install a CFW, you have to get ARM9 access. The current
method (jan. 2017) is through safehax.

# CFW

A Custom FirmWare (CFW) is actually a special program which modifies
an official firmware on-the-fly when the console is booting up. It can
remove signature checks or do other modifications.

True custom firmware (as in replacing the official firmware on the
NAND) is not yet possible because the Boot9 ROM (the portion of code
ran when the ARM9 processor boots up) checks the signature of the
firmware and stops if it isn't the right one.

SigHax (presented at 33c3) could potentially be used to sign custom
firmwares, but it isn't even close to being released. Developers need
a Boot9 ROM dump to work on and nobody's done it yet.
