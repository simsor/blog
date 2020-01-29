---
title: "AlexCTF Writeup"
date: 2017-02-08 17:01:11 +0100
draft: false
---

The only challenge I solved during this CTF was the "unVM_me" reverse
engineering challenge (finally! Something other than crypto!)

We were given a pyc (Python Bytecode) file containing the
flag. Executing it asked for the flag, and told us if it was right or
wrong.

<!-- more -->

## Decompiling the bytecode

I used [PyCDC](https://github.com/zrax/pycdc) to decompile the pyc
file. This gave me the following source code (I modified it to add
some error checking to help with debugging):

``` python
import md5
md5s = [
    0x831DAA3C843BA8B087C895F0ED305CE7L,
    0x6722F7A07246C6AF20662B855846C2C8L,
    0x5F04850FEC81A27AB5FC98BEFA4EB40CL,
    0xECF8DCAC7503E63A6A3667C5FB94F610L,
    0xC0FD15AE2C3931BC1E140523AE934722L,
    0x569F606FD6DA5D612F10CFB95C0BDE6DL,
    0x68CB5A1CF54C078BF0E7E89584C1A4EL,
    0xC11E2CD82D1F9FBD7E4D6EE9581FF3BDL,
    0x1DF4C637D625313720F45706A48FF20FL,
    0x3122EF3A001AAECDB8DD9D843C029E06L,
    0xADB778A0F729293E7E0B19B96A4C5A61L,
    0x938C747C6A051B3E163EB802A325148EL,
    0x38543C5E820DD9403B57BEFF6020596DL]
print 'Can you turn me back to python ? ...'
flag = raw_input('well as you wish.. what is the flag: ')
if len(flag) > 69:
    print 'nice try'
    exit()
if len(flag) % 5 != 0:
    print 'nice try'
    exit()
for i in range(0, len(flag), 5):
    s = flag[i:i + 5]
    if int('0x' + md5.new(s).hexdigest(), 16) != md5s[i / 5]:
        print "Error : %s" % (s)
        print "You entered : %s "% ('0x' + md5.new(s).hexdigest())
        print "Expected : %s " % (hex(md5s[i/5]))
        print 'nice try'
        exit()
        continue
print 'Congratz now you have the flag'
```

## Getting the flag

We can see a list of 13 MD5 hashes. The codes seems to check the MD5
hash of each group of 5 characters from the user string against the
corresponding hash in the list. This means we need to crack every hash
and that each should give us a 5-character string.

I used [HashKiller](https://hashkiller.co.uk/md5-decrypter.aspx) to
crack the hashes (I guess you could also try bruteforcing them, which
shouldn't be too long knowing the first characters were necessarily
`ALEXCTF{`)

This gave us the following flag: `ALEXCTF{dv5d4s2vj8nk43s8d8l6m1n5l67ds9v41n52nv37j481h3d28n4b6v3k}`

Inputting it back into the program proved it was indeed the correct
flag!
