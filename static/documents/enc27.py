#!/usr/bin/env python

def supa_encryption(data, key):
    res = [chr(0)]*24
    # [\0, \0, ... , \0]
    for i in range(len(res)):
        q = ord(data[i])
        d = ord(key[i])
        c = q ^ d
        res[i] = chr(c)
    res = ''.join(res)
    return res

def add_pad(msg):
    L = 24 - len(msg)%24
    msg += chr(L)*L
    return msg

if __name__ == "__main__":
    with open('fullhd.png','rb') as f:
        data = f.read()

    data = add_pad(data)

    
    with open('key.txt') as f:
        key = f.read()
    
    enc_data = ''
    for i in range(0, len(data), 24):
        enc = supa_encryption(data[i:i+24], key)
        enc_data += enc

    with open('BITSCTFfullhd.png', 'wb') as f:
        f.write(enc_data)

