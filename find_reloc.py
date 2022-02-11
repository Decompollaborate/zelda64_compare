#!/usr/bin/python3

import argparse
import os
import struct

# def readFile(filepath):
#     with open(filepath) as f:
#         return [x.strip() for x in f.readlines()]

# def readFileAsBytearray(filepath: str) -> bytearray:
#     if not os.path.exists(filepath):
#         return bytearray(0)
#     with open(filepath, mode="rb") as f:
#         return bytearray(f.read())

def getLastWord(filepath):
    with open(filepath, "rb") as f:
        f.seek(-4, os.SEEK_END)
        return struct.unpack('>I', bytes(f.read()))[0]

def determineIfReloc(filepath):
    lastWord = getLastWord(filepath)
    fileSize = os.stat(filepath).st_size

    if lastWord == fileSize:
        print(f"{os.path.split(filepath)[1]},{fileSize:X},reloc")
    else:
        print(f"{os.path.split(filepath)[1]},{fileSize:X},")

def main():
    description = "Finds files that look like ov."
    epilog = ""

    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("dir", help="Directory to search.")
    args = parser.parse_args()

    # dir = os.fsencode(args.dir)
        
    for file in os.listdir(args.dir):
        # filename = os.fsdecode(file)
        # print(filename)
        # determineIfReloc(file)
        determineIfReloc(os.path.join(args.dir, file))

if __name__ == "__main__":
    main()
