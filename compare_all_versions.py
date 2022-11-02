#!/usr/bin/env python3

from __future__ import annotations

import argparse
from multiprocessing import Pool, cpu_count
from functools import partial
from pathlib import Path
import spimdisasm

from mips.ZeldaTables import contextReadVariablesCsv, contextReadFunctionsCsv, getFileAddresses, FileAddressesEntry


def countUnique(row: list) -> int:
    unique = set(row)
    count = len(unique)
    if "" in unique:
        count -= 1
    return count

def removePointers(args, filedata: bytearray) -> bytearray:
    if args.dont_remove_ptrs:
        return filedata
    if not args.ignore04: # This will probably grow...
        return filedata

    words = spimdisasm.common.Utils.bytesToWords(filedata)
    for i in range(len(words)):
        w = words[i]
        if args.ignore04:
            if ((w >> 24) & 0xFF) == 0x04:
                words[i] = 0x04000000
    return spimdisasm.common.Utils.wordsToBytes(words, filedata)


def getHashesOfFiles(args, filesPath: list[Path]) -> list[str]:
    hashList = []
    for path in filesPath:
        f = spimdisasm.common.Utils.readFileAsBytearray(path)
        if len(f) != 0:
            fHash = spimdisasm.common.Utils.getStrHash(removePointers(args, f))
            line = fHash + " " + str(path) # To be consistent with runCommandGetOutput("md5sum", md5arglist)
            hashList.append(line)
    return hashList

def compareFileAcrossVersions(filename: str, game: str, versionsList: list[str], contextPerVersion: dict[str, spimdisasm.common.Context], fileAddressesPerVersion: dict, args) -> list[list[str]]:
    md5arglist = list(map(lambda orig_string: Path(game, orig_string, "baserom", filename), versionsList))
    # os.system( "md5sum " + " ".join(filesPath) )

    # Get hashes.
    # output = runCommandGetOutput("md5sum", filesPath)
    output = getHashesOfFiles(args, md5arglist)

    # Print md5hash
    #print("\n".join(output))
    #print()

    filesHashes = dict() # "NN0": "339614255f179a1e308d954d8f7ffc0a"
    firstFilePerHash = dict() # "339614255f179a1e308d954d8f7ffc0a": "NN0"

    for line in output:
        trimmed = spimdisasm.common.Utils.removeExtraWhitespace(line)
        filehash, filepath = trimmed.split(" ")
        version = filepath.split("/")[1]

        # Map each abbreviation and its hash.
        filesHashes[version] = filehash

        # Find out where in which version this hash appeared for first time.
        if filehash not in firstFilePerHash:
            firstFilePerHash[filehash] = version

    row = [filename]
    for ver in versionsList:
        if ver in filesHashes:
            fHash = filesHashes[ver]
            row.append(firstFilePerHash[fHash])
        else:
            row.append("")
    return [row]

def compareOverlayAcrossVersions(filename: str, game: str, versionsList: list[str], contextPerVersion: dict[str, spimdisasm.common.Context], fileAddressesPerVersion: dict[str, dict[str, FileAddressesEntry]], args) -> list[list[str]]:
    column = []
    filesHashes = dict() # "filename": {"NN0": hash}
    firstFilePerHash = dict() # "filename": {hash: "NN0"}

    if filename.startswith("#"):
        return column

    is_overlay = filename.startswith("ovl_")

    for version in versionsList:
        splitsData = None
        tablePath = Path(game, version, "tables", f"files_{filename}.csv")
        if tablePath.exists():
            # print(tablePath)
            splitsData = spimdisasm.common.FileSplitFormat()
            splitsData.readCsvFile(tablePath)

        path = Path(game, version, "baserom", filename)

        array_of_bytes = spimdisasm.common.Utils.readFileAsBytearray(path)
        if len(array_of_bytes) == 0:
            # print(f"Skipping {path}")
            continue

        if is_overlay:
            vramStart = -1
            if version in fileAddressesPerVersion:
                if filename in fileAddressesPerVersion[version]:
                    vramStart = fileAddressesPerVersion[version][filename].vramStart

            relocSection = spimdisasm.mips.sections.SectionRelocZ64(contextPerVersion[version], 0, len(array_of_bytes), vramStart, filename, array_of_bytes, 0, None)
            f = spimdisasm.mips.FileSplits(contextPerVersion[version], 0, len(array_of_bytes), vramStart, filename, array_of_bytes, 0, None, relocSection=relocSection)
        elif filename in ("code", "boot", "n64dd"):
            f = spimdisasm.mips.FileSplits(contextPerVersion[version], 0, len(array_of_bytes), -1, filename, array_of_bytes, 0, None, splitsData=splitsData)
        else:
            f = spimdisasm.mips.sections.SectionData(contextPerVersion[version], 0, len(array_of_bytes), 0, filename, array_of_bytes, 0, None)

        f.analyze()

        if spimdisasm.common.GlobalConfig.REMOVE_POINTERS:
            f.removePointers()

        if isinstance(f, spimdisasm.mips.FileSplits):
            subfiles = {
                ".text" : f.sectionsDict[spimdisasm.common.FileSectionType.Text],
                ".data" : f.sectionsDict[spimdisasm.common.FileSectionType.Data],
                ".rodata" : f.sectionsDict[spimdisasm.common.FileSectionType.Rodata],
                #".bss" : f.bss,
            }
        else:
            subfiles = {
                "" : {"": f},
            }

        for sectionName, sectionCat in subfiles.items():
            for name, sub in sectionCat.items():
                if is_overlay:
                    name = ""
                if name != "":
                    name = "." + name
                file_section = filename + name + sectionName
                if file_section not in filesHashes:
                    filesHashes[file_section] = dict()
                    firstFilePerHash[file_section] = dict()

                f_hash = sub.getHash()
                # Map each abbreviation to its hash.
                filesHashes[file_section][version] = f_hash

                # Find out where in which version this hash appeared for first time.
                if f_hash not in firstFilePerHash[file_section]:
                    firstFilePerHash[file_section][f_hash] = version

    for file_section in filesHashes:
        row = [file_section]
        for version in versionsList:
            if version in filesHashes[file_section]:
                fHash = filesHashes[file_section][version]
                row.append(firstFilePerHash[file_section][fHash])
            else:
                row.append("")
        column.append(row)

    return column


def main():
    parser = argparse.ArgumentParser()
    choices = ["oot", "mm"]
    parser.add_argument("game", help="Game to comapre.", choices=choices)
    parser.add_argument("versionlist", help="Path to version list.")
    parser.add_argument("filelist", help="list of filenames of the ROM that will be compared.")
    parser.add_argument("--noheader", help="Disables the csv header.", action="store_true")
    # parser.add_argument("--overlays", help="Treats the files in filelist as overlays.", action="store_true")
    parser.add_argument("--ignore-words", help="A space separated list of hex numbers. Word differences will be ignored that starts in any of the provided arguments. Max value: FF", action="extend", nargs="+")
    parser.add_argument("--ignore-branches", help="Ignores the address of every branch, jump and jal.", action="store_true")
    parser.add_argument("--dont-remove-ptrs", help="Disable the pointer removal feature.", action="store_true")
    parser.add_argument("--disable-multiprocessing", help="", action="store_true")
    args = parser.parse_args()

    spimdisasm.common.GlobalConfig.REMOVE_POINTERS = not args.dont_remove_ptrs
    spimdisasm.common.GlobalConfig.IGNORE_BRANCHES = args.ignore_branches
    if args.ignore_words:
        for upperByte in args.ignore_words:
            spimdisasm.common.GlobalConfig.IGNORE_WORD_LIST.add(int(upperByte, 16))
    # spimdisasm.common.GlobalConfig.ASM_COMMENT = True
    spimdisasm.common.GlobalConfig.PRODUCE_SYMBOLS_PLUS_OFFSET = True
    # spimdisasm.common.GlobalConfig.TRUST_USER_FUNCTIONS = True
    # spimdisasm.common.GlobalConfig.DISASSEMBLE_UNKNOWN_INSTRUCTIONS = args.disasm_unknown
    # spimdisasm.common.GlobalConfig.VERBOSE = args.verbose
    # spimdisasm.common.GlobalConfig.QUIET = args.quiet

    # Read filelist
    versionsList = []
    with open(args.versionlist) as f:
        for version in f:
            if version.startswith("#"):
                continue
            versionsList.append(version.strip())
    filesList = spimdisasm.common.Utils.readFile(args.filelist)

    contextPerVersion: dict[str, spimdisasm.common.Context] = dict()
    for version in versionsList:
        context = spimdisasm.common.Context()
        context.fillDefaultBannedSymbols()
        context.globalSegment.fillLibultraSymbols()
        context.globalSegment.fillHardwareRegs()
        # context.globalSegment.readFunctionMap(version)
        contextReadVariablesCsv(context, args.game, version)
        contextReadFunctionsCsv(context, args.game, version)
        contextPerVersion[version] = context

    fileAddressesPerVersion: dict[str, dict[str, FileAddressesEntry]] = dict()
    for version in versionsList:
        fileAddressesPerVersion[version] = getFileAddresses(Path(args.game, version, "tables", "file_addresses.csv"))

    if not args.noheader:
        # Print csv header
        print("File name", end="")
        for ver in versionsList:
            print("," + ver, end="")
        print(",Different versions", end="")
        print()

    # compareFunction = compareFileAcrossVersions
    # if args.overlays:
    #     compareFunction = compareOverlayAcrossVersions
    compareFunction = compareOverlayAcrossVersions

    if args.disable_multiprocessing:
        for filename in filesList:
            for row in compareFunction(filename, args.game, versionsList=versionsList, contextPerVersion=contextPerVersion, fileAddressesPerVersion=fileAddressesPerVersion, args=args):
                # Print csv row
                for cell in row:
                    print(cell + ",", end="")
                print(countUnique(row)-1)
    else:
        numCores = cpu_count()
        p = Pool(numCores)
        for column in p.imap(partial(compareFunction, game=args.game, versionsList=versionsList, contextPerVersion=contextPerVersion, fileAddressesPerVersion=fileAddressesPerVersion, args=args), filesList):
            for row in column:
                # Print csv row
                for cell in row:
                    print(cell + ",", end="")
                print(countUnique(row)-1)


if __name__ == "__main__":
    main()
