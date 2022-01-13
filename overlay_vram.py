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
        overlayVRAMDict[entry[0]] = [entry[2],entry[3]]

    for entry in dmadata:
        if not entry[0].startswith("ovl_"):
            continue
        
        # Get overlay VRAM from dict
        if entry[1] not in overlayVRAMDict:
            print("warning: " + entry[0] + " not found in overlay VRAM table", file=sys.stderr)
            continue
        entryVRAM = overlayVRAMDict[entry[1]]
        print(entry[0], end="")
        for column in entry[1:]:
            print(f",{column:X}", end="")
        for column in entryVRAM:
            print(f",{column:X}", end="")
        print("")
        



if __name__ == "__main__":
    main()
