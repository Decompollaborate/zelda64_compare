#!/usr/bin/python3

import argparse
import os
import struct

def readFile(filepath):
    with open(filepath) as f:
        return [x.strip() for x in f.readlines()]

def readFileAsBytearray(filepath: str) -> bytearray:
    if not os.path.exists(filepath):
        return bytearray(0)
    with open(filepath, mode="rb") as f:
        return bytearray(f.read())

def read_uint32_be(offset):
    return struct.unpack('>I', romData[offset:offset+4])[0]

def extract_dma(address):
    offset = address

    while True:
        fileVROMStart = read_uint32_be(offset)
        offset += 4
        fileVROMEnd = read_uint32_be(offset)
        offset += 4
        fileROMStart = read_uint32_be(offset)
        offset += 4
        fileROMEnd = read_uint32_be(offset)
        offset += 4

        if fileROMEnd != 0:
            compressed = True
        else:
            compressed = False

        fileName = nameData[(offset - address) // 0x10] if len(nameData) > 0 else ""
        if fileName != "":
            print(f"{fileName},", end="")
        else:
            print(f"file_{fileVROMStart:08X},", end="")

        print(f"{fileVROMStart:08X},{fileVROMEnd:08X},{fileROMStart:08X},{fileROMEnd:08X},{fileVROMEnd - fileVROMStart:6X},", end="")
        print(compressed)

        if read_uint32_be(offset) == 0:
            break

def main():
    description = "Extracts dmadata from a rom given the starting address."
    epilog = ""

    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("romfile", help="Rom from which to extract.")
    parser.add_argument("address", help="Rom address of first entry in table.")
    parser.add_argument("-n", "--namefile", help="Text file containing file names to use. If not specified, will use the vrom.")
    args = parser.parse_args()

    global romData
    global nameData

    nameData = []

    romData = readFileAsBytearray(args.romfile)

    if args.namefile != None:
        nameData = readFile(args.namefile)

    extract_dma(int(args.address, 16))

if __name__ == "__main__":
    main()
