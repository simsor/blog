---
title: "BITSCTF Writeup"
date: 2017-02-06 14:59:00 +0100
draft: false
---

Here's a quick writeup on the two challenges I solved (Banana Princess and Beginner's luck) during BITSCTF with the [Cryptis](https://bitsctf.bits-quark.org/team/157) team. It was my first CTF and a great experience :D

<!-- more -->

# Banana Princess

For this challenge, we were
given [a PDF file](/documents/MinionQuest.pdf) which was said to have
been encrypted.

## Hexdump, search for a header

By running `hexdump -C MinionQuest.pdf | head`, we can get the header of the PDF file.

    00000000  25 43 51 53 2d 31 2e 35  0d 25 e2 e3 cf d3 0d 0a  |%CQS-1.5.%......|
    00000010  34 20 30 20 62 6f 77 0d  3c 3c 2f 59 76 61 72 6e  |4 0 bow.<</Yvarn|
    00000020  65 76 6d 72 71 20 31 2f  59 20 34 33 30 31 39 30  |evmrq 1/Y 430190|
    00000030  2f 42 20 36 2f 52 20 34  30 34 33 34 33 2f 41 20  |/B 6/R 404343/A |
    00000040  31 2f 47 20 34 32 39 39  39 31 2f 55 20 5b 20 35  |1/G 429991/U [ 5|
    00000050  37 36 20 31 35 35 5d 3e  3e 0d 72 61 71 62 6f 77  |76 155]>>.raqbow|
    00000060  0d 20 20 20 20 20 20 20  20 20 20 20 20 20 20 20  |.               |
    00000070  20 20 0d 0a 6b 65 72 73  0d 0a 34 20 31 34 0d 0a  |  ..kers..4 14..|
    00000080  30 30 30 30 30 30 30 30  31 36 20 30 30 30 30 30  |0000000016 00000|
    00000090  20 61 0d 0a 30 30 30 30  30 30 30 37 33 31 20 30  | a..0000000731 0|

We can see the header is `CQS-1.5`. A normal PDF file header is
`PDF-1.5` (I used a reference PDF file to find this). 

## Find the encryption method

By inputting CQS into <http://www.dcode.fr/chiffre-cesar>,
we can see that a rotation of 13 gives us `PDF`.

## Unencrypt it

The file may have been encrypted by using a Caesar cipher on the
letters and leaving everything else alone. I wrote a Python script
to unencrypt it.

```python
#!/usr/bin/env python2
   
import codecs
    
res = ""
with open("MinionQuest.pdf2", "r") as f, open("result.pdf", "w") as out:
    for b in f.read():
        if ord(b) in range(ord("a"), ord("z")+1) or ord(b) in range(ord("A"), ord("Z")+1):
            # Then b = letter
            b = codecs.encode(b, "rot_13")
        res += b
    
    out.write(res)
```

The resulting PDF file had a message with a black bar over the key. 

## Extracting the key

I extracted the images using `pdfimages` :

    pdfimages -png result.pdf images

The first image had the key written on it! `BITSCTF{save_the_kid}`

# Beginner's luck

This challenge gave a [PNG file](/documents/BITSCTFfullhd.png) and [some encryption code](/documents/enc27.py). The goal was to find a flaw in the encryption to decrypt the file and get the key!

## Analysing the encryption code

The encryption code provided with the challenge was a pretty
straightforward XOR-cipher with a 24-byte long key.

The only working attack against this is a known-cleartext attack.

## Reading up on the PNG file format & counting bytes

Fortunately for us, [PNG files have a fixed header](http://www.libpng.org/pub/png/spec/1.2/PNG-Structure.html), so it's pretty
easy to get the first 8 bytes of the key. [The IHDR header is also
always at the same place](http://stackoverflow.com/a/5354562)&#x2026;4 more bytes!

We can also guess the size of the picture, as the filename is
`fullhd.png`, we can assume the size is 1920x1080. That's 8 more
bytes!

Finally, I had to guess the size of the IHDR header&#x2026;got it first
try (0x0D)! That's another 4 bytes :D

`8 + 4 + 8 + 4 = 24` 

=> We've got the full key.

## Cracking the key and decrypting

The program then uses that key to decrypt the file.

```python
#!/usr/bin/env python
# coding: utf-8

from enc27 import supa_encryption

with open("BITSCTFfullhd.png", "rb") as f:
    txt = f.read()

known_offsets = {
    # Magic sequence
    0: 0x89,
    1: 0x50,
    2: 0x4E,
    3: 0x47,
    4: 0x0D,
    5: 0x0A,
    6: 0x1A,
    7: 0x0A,
    
    # IHDR length
    8: 0x00,
    9: 0x00,
    10: 0x00,
    11: 0x0d,
    
    # IHDR
    12: 0x49,
    13: 0x48,
    14: 0x44,
    15: 0x52,
    
    # Width: 1920
    16: 0x00,
    17: 0x00,
    18: 0x07,
    19: 0x80,
    
    # Height: 1080
    20: 0x00,
    21: 0x00,
    22: 0x04,
    23: 0x38
}
key = ["ø"] * 24
i = 0

for b in txt:
    if i in known_offsets.keys():
        q = known_offsets[i]
        c = ord(b)
    
        d = c ^ q
        keyidx = i % 24
        key[keyidx] = chr(d)
    i += 1
    
print("Key found: %s" % (''.join(key)))

with open('BITSCTFfullhd.png','rb') as f:
    data = f.read()
    
enc_data = ''
for i in range(0, len(data), 24):
    enc = supa_encryption(data[i:i+24], key)
    enc_data += enc
    
with open('fullhd.png', 'wb') as f:
    f.write(enc_data)
```

The image file has the flag handwritten in it: `BITSCTF{p_en_gee}`

The encryption key was `rkh%QP4g0&3g46@4*%f(UN#\`
