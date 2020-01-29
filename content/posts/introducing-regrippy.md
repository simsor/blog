---
title: "Introducing RegRippy"
date: 2019-04-19 09:32:12
draft: false
---

*This post was written as part of my work as a member of the [Airbus CERT](https://www.trusted-introducer.org/directory/teams/ai-cert.html). Anectodes and opinions shared in this post only reflect my own beliefs and not necessarily my teammates’ or my employer’s.*

When investigating an intrusion on a system, the Windows registry can be a treasure mine of information. From quick wins like grabbing the machine’s name or recent documents to more advanced techniques like parsing [shellbags](http://www.williballenthin.com/forensics/shellbags/index.html), you can get some very deep insight on what a machine was used for. The only trouble is to know where to look.

## The past

When performing DFIR, I regularly used [Regripper](https://github.com/keydet89/RegRipper2.8), which is a collection of Perl scripts to extract various information from registry [hives](https://docs.microsoft.com/en-us/windows/desktop/sysinfo/registry-hives). It worked decently enough, but there was a kind of unwieldy feeling to it. First of all, the `rip.pl` script wasn’t really happy to be called from anywhere other than its project folder. Wrapping it up in a shell script to fix it meant I had to provide the absolute path to the hive I wanted to analyze. Finally, it being written in Perl meant that I wasn’t confortable at all writing my own plugins for it.

All these seemingly small problems, when added together, meant that I was ready to move to an alternative. The only problem was, what alternative? Indeed, most registry analysis scripts were one-offs meant to grab a specific information from a hive, nothing else. There was no unified output between the tools, and each one used its own library or techniques to access the data it needed. That’s when I decided I needed to [write something myself](https://xkcd.com/927/).

## RegRippy - hopefully a better solution (r)

[RegRippy](https://github.com/airbus-cert/regrippy) is a collection of scripts as well as a framework to quickly extract data from Windows registry hives. It is written in Python 3 and uses William Ballenthin’s excellent [python-registry](https://github.com/williballenthin/python-registry) library to do most of the heavy lifting. It has lots of quality-of-life improvements over regripper, for example:
* Automatically pass the right hive to a plugin depending on which one it needs
* Read hives’ path from environment variables (`export` them once and there you go!)
* Find hives automatically if you pass the root directory of your disk
* Execute a plugin on every user hive (`NTUSER.DAT` or `UsrClass.dat`)
* Bodyfile format when piping through other commands
* And more!

I’ve also taken the time to fix all pet peeves I had with regripper, like the useless message when you ran a plugin or the problems regarding the `plugins` folder. RegRippy results are straight and to the point (most of the time). If you love timelining, you’re in luck! All plugins are also required to support a « machine-readable » output, which here means `Bodyfile` format! Pipe it straight into `mactime` and enjoy.

Here’s a sample session:
```
$ pip3 install regrippy
$ cd /mnt/c
$ reg_compname --root .
SIMON-LAPTOP
$
```
