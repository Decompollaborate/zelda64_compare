#!/usr/bin/python3

from __future__ import annotations

import argparse

from py_mips_disasm.mips.Utils import *

from mips.MipsSplitEntry import readSplitsFromCsv

def split_fileSplits(game: str, seg: str):
    sections = ["text", "data", "rodata", "bss"]

    tablePerVersion = dict()

    for section in sections:
        csvPath = os.path.join(game, "tables", f"{seg}.{section}.csv")

        if not os.path.exists(csvPath):
            continue

        splits = readSplitsFromCsv(csvPath)
        # print(splits)

        for version, files in splits.items():
            # print(version)

            if version == "":
                continue

            if version not in tablePerVersion:
                tablePerVersion[version] = []
            else:
                tablePerVersion[version].append("\n")
            tablePerVersion[version].append(f"offset,vram,.{section}\n")

            auxList = []

            for filename, splitData in files.items():
                # print("\t", filename, splitData)
                if splitData.offset < 0 or splitData.vram < 0 or splitData.filename == "":
                    continue
                auxList.append((splitData.offset, splitData.vram, splitData.size, splitData.filename))

            # fake extra to avoid problems
            auxList.append((0xFFFFFF, 0x80FFFFFF, 0, "end"))

            # Reading from the file may not be sorted by offset
            auxList.sort()

            i = 0
            while i < len(auxList) - 1:
                offset, vram, size, filename = auxList[i]
                nextOffset, _, _, _ = auxList[i+1]

                end = offset + size
                if size <= 0:
                    end = nextOffset

                if end < nextOffset:
                    # Adds missing files
                    auxList.insert(i+1, (end, vram + (end - offset), -1, f"file_{end:06X}"))

                tablePerVersion[version].append(f"{offset:X},{vram:X},{filename}\n")

                i += 1


    for version, lines in tablePerVersion.items():
        with open(os.path.join(game, version, "tables", f"files_{seg}.csv"), "w") as f:
            f.writelines(lines)


def split_functions(game: str):
    csvPath = os.path.join(game, "tables", "functions.csv")

    tablePerVersion = dict()

    functions = readCsv(csvPath)
    header = functions[0][2:]
    for i in range(2, len(functions)):
        funcName, _, *data = functions[i]

        for headerIndex, version in enumerate(header):
            if version not in tablePerVersion:
                tablePerVersion[version] = []

            vram = data[headerIndex]
            if vram == "":
                continue

            tablePerVersion[version].append(f"{vram},{funcName}\n")

    for version, lines in tablePerVersion.items():
        with open(os.path.join(game, version, "tables", "functions.csv"), "w") as f:
            f.writelines(lines)


def split_variables(game: str):
    csvPath = os.path.join(game, "tables", "variables.csv")

    tablePerVersion = dict()

    variables = readCsv(csvPath)
    header = variables[0][3:]
    for i in range(2, len(variables)):
        varName, type, _, *data = variables[i]

        for headerIndex, version in enumerate(header[::2]):
            if version not in tablePerVersion:
                tablePerVersion[version] = []

            # print(varName, version, data)
            vram, size = data[2*headerIndex : 2*headerIndex + 2]
            if vram == "":
                continue
            if size == "":
                size = "4"

            tablePerVersion[version].append(f"{vram},{varName},{type},0x{size}\n")

    for version, lines in tablePerVersion.items():
        with open(os.path.join(game, version, "tables", "variables.csv"), "w") as f:
            f.writelines(lines)


def main():
    description = ""

    epilog = f"""\
    """
    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    choices = ["oot", "mm"]
    parser.add_argument("game", help="Game to extract.", choices=choices)
    parser.add_argument("csv", help="") # TODO
    args = parser.parse_args()

    seg = os.path.split(args.csv)[-1].split('.')[0]

    if seg == "functions":
        split_functions(args.game)
    if seg == "variables":
        split_variables(args.game)
    else:
        split_fileSplits(args.game, seg)


if __name__ == "__main__":
    main()
