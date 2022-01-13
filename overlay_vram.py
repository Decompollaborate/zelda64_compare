#! /usr/bin/env python3

# Consider merging this script with vram.py, since that is doing almost all of the work.

import argparse
import csv
import vram
import sys

def main():
    description = "Uses dmadata and dlftbls to find "

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("game", help="Game to use.")
    parser.add_argument("dmadata", help="dmadata csv to use.")
    parser.add_argument("code", help="code file to use to find overlay data")
    # parser.add_argument("--outFile", help="File to write to", default=sys.stdout)
    args = parser.parse_args()

    with open(args.dmadata, "r") as f:
        dmalist = list(csv.reader(f))

    dmadata = []
    for entry in dmalist:
        dmadata.append([entry[0], *map(lambda x: int(x, 16), entry[1:])])

    overlayTable = vram.constructOverlayTable(args.code, args.game)

    overlayVRAMDict = {}
    for entry in overlayTable:
        overlayVRAMDict[entry[0]] = entry[2:]


    print("File name,VROM start,VROM end,ROM start,ROM end,Size (VROM),Compressed?,VRAM start,VRAM end,Size (VRAM),bss,type,number")

    for entry in dmadata:
        # Name
        print(entry[0], end="")

        # VROM/ROM
        for column in entry[1:]:
            print(f",{column:X}", end="")

        sizeVROM = entry[2] - entry[1]
        print(f",{sizeVROM:X}", end="")
        # Compressed?
        print(",N" if entry[4] == 0 else ",Y", end="")

        # Skip rest for non-overlays
        if entry[0].startswith("ovl_"):
        # Get overlay VRAM from dict
            if entry[1] not in overlayVRAMDict:
                print("")
                print("warning: " + entry[0] + " not found in overlay VRAM table", file=sys.stderr)
                continue
            entryVRAMStart, entryVRAMEnd, entryVRAMType, entryVRAMNumber = overlayVRAMDict[entry[1]]
            print(f",{entryVRAMStart:X}", end="")
            print(f",{entryVRAMEnd:X}", end="")

            sizeVRAM = entryVRAMEnd-entryVRAMStart
            print(f",{sizeVRAM:X}", end="")

            # Size of bss is extra VRAM
            print(f",{sizeVRAM - sizeVROM:X}", end="")

            # 
            print(',' + entryVRAMType, end="")
            print(f",{entryVRAMNumber:X}", end="")

        else:
            print(",,,,,", end="")
            if entry[0].startswith("object_") or entry[0].startswith("gameplay_") or entry[0] == "link_animetion":
                print("object,", end="")
            elif entry[0].startswith("g_pn_"):
                print("titlecard,", end="")
            elif entry[0].startswith("vr_"):
                print("skybox,", end="")
            elif entry[0].startswith("Z2_") or entry[0].endswith("_scene"):
                print("scene,", end="")
            elif "room" in entry[0]:
                print("room,", end="")
            elif entry[0].startswith("anime_") or entry[0].startswith("bump_") or entry[0].startswith("softsprite_"):
                print("segment,", end="")


        print("")




if __name__ == "__main__":
    main()
