#! /usr/env/bin python3

import struct
import sys

def as_word(b, off=0):
    return struct.unpack(">I", b[off:off+4])[0]

def calc_crc(rom_data, cic_type):
    start = 0x1000
    end = 0x101000

    unsigned_long = lambda i: i & 0xFFFFFFFF
    rol = lambda i, b: unsigned_long(i << b) | (i >> (-b & 0x1F))

    if cic_type == 6101 or cic_type == 6102:
        seed = 0xF8CA4DDC
    elif cic_type == 6103:
        seed = 0xA3886759
    elif cic_type == 6105:
        seed = 0xDF26F436
    elif cic_type == 6106:
        seed = 0x1FEA617A
    else:
        assert False , f"Unknown cic type: {cic_type}"

    t1 = t2 = t3 = t4 = t5 = t6 = seed

    for pos in range(start, end, 4):
        d = as_word(rom_data, pos)
        r = rol(d, d & 0x1F)

        t6d = unsigned_long(t6 + d)
        if t6d < t6:
            t4 = unsigned_long(t4 + 1)
        t6 = t6d
        t3 ^= d
        t5 = unsigned_long(t5 + r)

        if t2 > d:
            t2 ^= r
        else:
            t2 ^= t6 ^ d

        if cic_type == 6105:
            t1 = unsigned_long(t1 + (as_word(rom_data, 0x0750 + (pos & 0xFF)) ^ d))
        else:
            t1 = unsigned_long(t1 + (t5 ^ d))

    chksum = [0,0]

    if cic_type == 6103:
        chksum[0] = unsigned_long((t6 ^ t4) + t3)
        chksum[1] = unsigned_long((t5 ^ t2) + t1)
    elif cic_type == 6106:
        chksum[0] = unsigned_long((t6 * t4) + t3)
        chksum[1] = unsigned_long((t5 * t2) + t1)
    else:
        chksum[0] = t6 ^ t4 ^ t3
        chksum[1] = t5 ^ t2 ^ t1

    return struct.pack(">II", chksum[0], chksum[1])

def main():
    romFileName = sys.argv[1]
    with open(romFileName, mode="rb") as f:
        fileContent = f.read()
        new_crc = calc_crc(fileContent, 6105)
        print(new_crc.hex())


if __name__ == "__main__":
    main()
