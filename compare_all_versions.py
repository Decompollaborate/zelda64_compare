#!/usr/bin/python3

from __future__ import annotations

import argparse
import os
from typing import List, Dict
from multiprocessing import Pool, cpu_count
from functools import partial

from py_mips_disasm.mips.Utils import *
from py_mips_disasm.mips.GlobalConfig import GlobalConfig
from py_mips_disasm.mips.MipsSection import Section
from py_mips_disasm.mips.MipsContext import Context
from py_mips_disasm.mips.FileSplitFormat import FileSplitFormat, FileSectionType

from mips.MipsFileGeneric import FileGeneric
from mips.MipsFileOverlay import FileOverlay
from mips.MipsFileSplits import FileSplits
from mips.ZeldaTables import OverlayTableEntry, contextReadVariablesCsv, contextReadFunctionsCsv, getDmaAddresses, DmaEntry
from mips import ZeldaOffsets


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

    words = bytesToBEWords(filedata)
    for i in range(len(words)):
        w = words[i]
        if args.ignore04:
            if ((w >> 24) & 0xFF) == 0x04:
                words[i] = 0x04000000
    return beWordsToBytes(words, filedata)


def getHashesOfFiles(args, filesPath: List[str]) -> List[str]:
    hashList = []
    for path in filesPath:
        f = readFileAsBytearray(path)
        if len(f) != 0:
            fHash = getStrHash(removePointers(args, f))
            line = fHash + " " + path # To be consistent with runCommandGetOutput("md5sum", md5arglist)
            hashList.append(line)
    return hashList

def compareFileAcrossVersions(filename: str, game: str, versionsList: List[str], contextPerVersion: Dict[str, Context], dmaAddresses: dict, actorOverlayTable: dict, args) -> List[List[str]]:
    md5arglist = list(map(lambda orig_string: game + "/" + orig_string + "/" + "baserom" + "/" + filename, versionsList))
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
        trimmed = removeExtraWhitespace(line)
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

def compareOverlayAcrossVersions(filename: str, game: str, versionsList: List[str], contextPerVersion: Dict[str, Context], dmaAddresses: Dict[str, Dict[str, DmaEntry]], actorOverlayTable: Dict[str, List[OverlayTableEntry]], args) -> List[List[str]]:
    column = []
    filesHashes = dict() # "filename": {"NN0": hash}
    firstFilePerHash = dict() # "filename": {hash: "NN0"}

    if filename.startswith("#"):
        return column

    is_overlay = filename.startswith("ovl_")

    for version in versionsList:
        splitsData = None
        tablePath = os.path.join(game, version, "tables", f"files_{filename}.csv")
        if os.path.exists(tablePath):
            # print(tablePath)
            splitsData = FileSplitFormat(tablePath)

        path = os.path.join(game, version, "baserom", filename)

        array_of_bytes = readFileAsBytearray(path)
        if len(array_of_bytes) == 0:
            # print(f"Skipping {path}")
            continue

        if is_overlay:
            tableEntry = None
            if version in dmaAddresses:
                versionData = dmaAddresses[version]
                if filename in versionData:
                    dmaData = versionData[filename]
                    if version in actorOverlayTable:
                        for entry in actorOverlayTable[version]:
                            if entry.vromStart == dmaData.vromStart:
                                tableEntry = entry
                                break

            f = FileOverlay(array_of_bytes, filename, version, contextPerVersion[version], tableEntry=tableEntry)
        elif filename in ("code", "boot", "n64dd"):
            f = FileSplits(array_of_bytes, filename, version, contextPerVersion[version], splitsData)
        else:
            f = Section(array_of_bytes, filename, version, contextPerVersion[version])

        f.analyze()

        if GlobalConfig.REMOVE_POINTERS:
            was_updated = f.removePointers()
            if was_updated:
                f.updateBytes()

        if isinstance(f, FileGeneric):
            subfiles = {
                ".text" : f.sectionsDict[FileSectionType.Text],
                ".data" : f.sectionsDict[FileSectionType.Data],
                ".rodata" : f.sectionsDict[FileSectionType.Rodata],
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
    parser.add_argument("filelist", help="List of filenames of the ROM that will be compared.")
    parser.add_argument("--noheader", help="Disables the csv header.", action="store_true")
    # parser.add_argument("--overlays", help="Treats the files in filelist as overlays.", action="store_true")
    parser.add_argument("--ignore-words", help="A space separated list of hex numbers. Word differences will be ignored that starts in any of the provided arguments. Max value: FF", action="extend", nargs="+")
    parser.add_argument("--ignore-branches", help="Ignores the address of every branch, jump and jal.", action="store_true")
    parser.add_argument("--dont-remove-ptrs", help="Disable the pointer removal feature.", action="store_true")
    parser.add_argument("--disable-multiprocessing", help="", action="store_true")
    args = parser.parse_args()

    GlobalConfig.REMOVE_POINTERS = not args.dont_remove_ptrs
    GlobalConfig.IGNORE_BRANCHES = args.ignore_branches
    if args.ignore_words:
        for upperByte in args.ignore_words:
            GlobalConfig.IGNORE_WORD_LIST.add(int(upperByte, 16))
    # GlobalConfig.ASM_COMMENT = True
    GlobalConfig.PRODUCE_SYMBOLS_PLUS_OFFSET = True
    # GlobalConfig.TRUST_USER_FUNCTIONS = True
    # GlobalConfig.DISASSEMBLE_UNKNOWN_INSTRUCTIONS = args.disasm_unknown
    # GlobalConfig.VERBOSE = args.verbose
    # GlobalConfig.QUIET = args.quiet

    # Read filelist
    versionsList = []
    with open(args.versionlist) as f:
        for version in f:
            if version.startswith("#"):
                continue
            versionsList.append(version.strip())
    filesList = readFile(args.filelist)

    contextPerVersion: Dict[str, Context] = dict()
    for version in versionsList:
        context = Context()
        context.fillDefaultBannedSymbols()
        context.fillLibultraSymbols()
        context.fillHardwareRegs()
        context.readFunctionMap(version)
        contextReadVariablesCsv(context, args.game, version)
        contextReadFunctionsCsv(context, args.game, version)
        contextPerVersion[version] = context

    dmaAddresses: Dict[str, Dict[str, DmaEntry]] = dict()
    actorOverlayTable: Dict[str, List[OverlayTableEntry]] = dict()
    for version in versionsList:
        dmaAddresses[version] = getDmaAddresses(args.game, version)

        codePath = os.path.join(args.game, version, "baserom", "code")

        if os.path.exists(codePath) and version in ZeldaOffsets.offset_ActorOverlayTable[args.game]:
            tableOffset = ZeldaOffsets.offset_ActorOverlayTable[args.game][version]
            if tableOffset != 0x0 and tableOffset != 0xFFFFFF:
                codeData = readFileAsBytearray(codePath)
                i = 0
                table = list()
                while i < ZeldaOffsets.ActorIDMax[args.game]:
                    entry = OverlayTableEntry(codeData[tableOffset + i*0x20 : tableOffset + (i+1)*0x20])
                    table.append(entry)
                    i += 1
                actorOverlayTable[version] = table

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
            for row in compareFunction(filename, args.game, versionsList=versionsList, contextPerVersion=contextPerVersion, dmaAddresses=dmaAddresses, actorOverlayTable=actorOverlayTable, args=args):
                # Print csv row
                for cell in row:
                    print(cell + ",", end="")
                print(countUnique(row)-1)
    else:
        numCores = cpu_count()
        p = Pool(numCores)
        for column in p.imap(partial(compareFunction, game=args.game, versionsList=versionsList, contextPerVersion=contextPerVersion, dmaAddresses=dmaAddresses, actorOverlayTable=actorOverlayTable, args=args), filesList):
            for row in column:
                # Print csv row
                for cell in row:
                    print(cell + ",", end="")
                print(countUnique(row)-1)


if __name__ == "__main__":
    main()
