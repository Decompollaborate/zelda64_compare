#!/usr/bin/env python3

import argparse
import mmap
import os
import struct

def main():
    description = "Find the archives used by Yoshi's Story and (for now) print their information"
    epilog = ""

    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("rom", help="rom file to read.")
    
    args = parser.parse_args()

    with open(args.rom, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0)

    offset = -1
    while True:
        cmprBytes = "CMPR".encode()
        offset = mm.find(cmprBytes, offset + 1)
        if offset == -1:
            break

        mm.seek(offset, os.SEEK_SET)
        print(f"{offset:X},", end="")
        headers = struct.unpack_from(">4sII4x6s2xII", mm, offset=offset)
        print("{1:X},{2:X},{4:X},{5:X}".format(*headers))

        # break



if __name__ == "__main__":
    main()
