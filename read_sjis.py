#!/usr/bin/env python3

import argparse
import os

def read_data(file, start, end):
        
    with open(file, "rb") as f:
        f.seek(start, os.SEEK_SET)
        if end == 0:
            return f.read()
        else:
            return f.read(end - start)

def main():
    description = ""
    epilog = ""

    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("file", help="file to read.")
    parser.add_argument("-s", "--start", help="Start of chunk to read.")
    parser.add_argument("-e", "--end", help="End of chunk to read.")
    
    args = parser.parse_args()

    start = int(args.start, 0) if args.start else 0
    end = int(args.end, 0) if args.end else 0

    print(f"{start:X},{end:X}")

    bytes = read_data(args.file, start, end)
    print(f"{len(bytes):X}")
    for byte in bytes:
        print(f"{byte:02X} ", end="")
    print()

    i = 0
    while bytes[i:i+2] != bytes.fromhex("8170"):
        # print(f"{i} :", end="")
        try:
            print(bytes[i:i+2].decode("shift-jis"), end="")
        except UnicodeDecodeError:
            print(f"|\\x{bytes[i]:02X} \\x{bytes[i+1]:02X}|", end="")
        # ch = bytes[i:i+2].decode("shift-jis")
        # print(ch, end="")
        i += 2
    print("END")



if __name__ == "__main__":
    main()
