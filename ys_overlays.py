#!/usr/bin/env python3

import argparse
import mmap
import struct

# This does assume the first reloc occurs at an offset < 0xFFFF, which seems reasonable
relocTypes = {
    b"\x44\x00": "text_26",
    b"\x45\x00": "text_HI16",
    b"\x46\x00": "text_LO16",
    b"\x82\x00": "data_32",
    b"\xC2\x00": "rodata_32",
}

emptyOvl = bytes.fromhex("00000000000000000000000000000020")

def main():
    description = "Find all the Z64-style overlays in an uncompressed ROM. dmadata not required."
    epilog = ""

    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("rom", help="rom file to read.")
    
    args = parser.parse_args()

    # Faster than just reading everything into RAM
    with open(args.rom, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0)

    # print column headers
    print(f"fileRomStart,fileRomEnd,textSize,dataSize,rodataSize,bssSize,ovlSize,relocCount")

    doubleO = b"\x00\x00"
    prevFileEnd = 0
    # makerom contains no overlays
    start = 0x1000
    length = len(mm)

    # iterate over ROM looking for .ovl sections. They should be 0x10-aligned, so only need to work in blocks of 0x10
    while start < length:
        # Look for section sizes first
        j = 0

        # overlays should never have section sizes > 0xFFFFFF (16 MB!). Just check the top byte for speed.
        while j < 0x14:
            if mm[ start + j ] != 0:
                break
            j += 4
        # I.e. one int is too big to be a section size.
        if j < 0x14:
            start += 0x10
            continue
        # Next word after section size is not a reloc, or section is not just empty
        if mm[ start + 0x14 : start + 0x14 + 2 ] not in relocTypes and mm[ start + 0x10 : start + 0x20 ] != emptyOvl:
            start += 0x10
            continue

        
        # Use reloc count to determine putative .ovl setion size
        count = struct.unpack_from(">I", mm[ start + 0x10 : ])[0]
        end = start + 4 * count + 0x14
        end = ((end + 4 + 0xF) & ~0xF)
        # .ovl section should be no larger than 0xFFFF (MM Player's is 0x43F0)
        if mm[ end - 4 : end - 2 ] != doubleO:
            start += 0x10
            continue
        
        fileRomEnd = end
        ovlSize = struct.unpack_from(">I", mm[ end - 4 : ])[0]
        # .ovl section should report its own size as the last word
        if ovlSize != end - start:
            start += 0x10
            continue

        ovlStart = fileRomEnd - ovlSize
        textSize, dataSize, rodataSize, bssSize, relocCount = struct.unpack_from(">IIIII", mm[ovlStart:])
        fileRomStart = ovlStart - textSize - dataSize - rodataSize
        # Sections should all be 0x10-aligned
        if textSize & 0xF or dataSize & 0xF or rodataSize & 0xF or bssSize & 0xF:
            start += 0x10
            continue

        print(f"{fileRomStart:X},{fileRomEnd:X},{textSize:X},{dataSize:X},{rodataSize:X},{bssSize:X},{ovlSize:X},{relocCount},{fileRomStart-prevFileEnd:X}")

        prevFileEnd = fileRomEnd
        start = fileRomEnd



if __name__ == "__main__":
    main()
