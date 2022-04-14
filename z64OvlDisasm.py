#! /usr/bin/env python3

from __future__ import annotations

import argparse
import os
from typing import List, Tuple

import py_mips_disasm.backend.common.Utils as disasm_Utils
from py_mips_disasm.backend.common.GlobalConfig import GlobalConfig, printQuietless, printVerbose
from py_mips_disasm.backend.common.Context import Context
from py_mips_disasm.backend.common.FileSectionType import FileSectionType
from py_mips_disasm.backend.common.FileSplitFormat import FileSplitFormat

from py_mips_disasm.backend.mips.MipsText import Text
from py_mips_disasm.backend.mips.MipsRodata import Rodata
from py_mips_disasm.backend.mips.FilesHandlers import writeSplitedFunction, writeOtherRodata

from mips.MipsFileOverlay import FileOverlay
from mips.ZeldaTables import getFileAddresses

def writeFiles(ovlSection: FileOverlay, textOutput: str, dataOutput: str|None):
    printVerbose("Writing files...")

    if dataOutput is None:
        dataOutput = textOutput

    textOutput += "/"
    dataOutput += "/"

    head, tail = os.path.split(textOutput)

    # Create directories
    if head != "":
        os.makedirs(head, exist_ok=True)

    head, tail = os.path.split(dataOutput)

    # Create directories
    if head != "":
        os.makedirs(head, exist_ok=True)

    for subFileName, section in ovlSection.sectionsDict[FileSectionType.Text].items():
        section.saveToFile(os.path.join(textOutput, subFileName))

    for sectionType, filesinSection in ovlSection.sectionsDict.items():
        if sectionType == FileSectionType.Text:
            continue
        for subFileName, section in filesinSection.items():
            section.saveToFile(os.path.join(dataOutput, subFileName))

    ovlSection.reloc.saveToFile(dataOutput + ovlSection.reloc.filename)


# Return the name of the file after the overlay file, which is its reloc file in Animal Forest
def findRelocFile(input_name: str, file_addresses: str) -> str:
    if file_addresses is not None and os.path.exists(file_addresses):
        with open(file_addresses) as f:
            header = True
            retNext = False
            for line in f:
                if header:
                    # Skip csv header
                    header = False
                    continue
                if retNext:
                    return line.strip().split(",")[0]
                filename = line.strip().split(",")[0]
                if input_name == filename:
                    retNext = True
    raise RuntimeError("Relocation file not found.")


def ovlDisassemblerMain():
    description = ""
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument("binary", help="Path to input binary")
    parser.add_argument("output", help="Path to output. Use '-' to print to stdout instead")

    parser.add_argument("-r", "--reloc-separate", help="Should look for separate relocation file", action="store_true")

    parser.add_argument("--data-output", help="Path to output the data and rodata disassembly")

    parser.add_argument("--file-splits", help="Path to a file splits csv")

    parser.add_argument("--file-addresses", help="Path to a csv with the addresses of every file")

    parser.add_argument("--split-functions", help="Enables the function and rodata splitter. Expects a path to place the splited functions", metavar="PATH")

    parser.add_argument("--nuke-pointers", help="Use every technique available to remove pointers", action="store_true")

    Context.addParametersToArgParse(parser)

    GlobalConfig.addParametersToArgParse(parser)

    parser.add_argument("--add-filename", help="Adds the filename of the file to the generated function/variable name")

    args = parser.parse_args()

    GlobalConfig.parseArgs(args)

    GlobalConfig.REMOVE_POINTERS = args.nuke_pointers
    GlobalConfig.IGNORE_BRANCHES = args.nuke_pointers
    if args.nuke_pointers:
        GlobalConfig.IGNORE_WORD_LIST.add(0x80)

    GlobalConfig.PRODUCE_SYMBOLS_PLUS_OFFSET = True
    GlobalConfig.TRUST_USER_FUNCTIONS = True


    context = Context()
    context.parseArgs(args)

    array_of_bytes = disasm_Utils.readFileAsBytearray(args.binary)
    input_name = os.path.splitext(os.path.split(args.binary)[1])[0]


    splitsData = None
    if args.file_splits is not None and os.path.exists(args.file_splits):
        splitsData = FileSplitFormat()
        splitsData.readCsvFile(args.file_splits)

    fileAddresses = getFileAddresses(args.file_addresses)

    if args.reloc_separate:
        reloc_filename = findRelocFile(input_name, args.file_addresses)
        reloc_path = os.path.join(os.path.split(args.binary)[0],reloc_filename)
        # print(reloc_path)
        array_of_bytes.extend(disasm_Utils.readFileAsBytearray(reloc_path))


    vramStart = -1
    if input_name in fileAddresses:
        vramStart = fileAddresses[input_name].vramStart

    f = FileOverlay(array_of_bytes, input_name, context, splitsData=splitsData, vramStartParam=vramStart)

    f.analyze()

    f.updateCommentOffset()

    if GlobalConfig.VERBOSE:
        for sectDict in f.sectionsDict.values():
            for section in sectDict.values():
                section.printAnalyzisResults()

    if args.nuke_pointers:
        printVerbose("Nuking pointers...")
        f.removePointers()

    writeFiles(f, args.output, args.data_output)

    if args.split_functions is not None:
        printVerbose("Spliting functions")
        rodataList: List[Tuple[str, Rodata]] = list()
        for rodataName, rodataSection in f.sectionsDict[FileSectionType.Rodata].items():
            assert(isinstance(rodataSection, Rodata))
            rodataList.append((rodataName, rodataSection))
        for path, subFile in f.sectionsDict[FileSectionType.Text].items():
            assert(isinstance(subFile, Text))
            for func in subFile.functions:
                writeSplitedFunction(os.path.join(args.split_functions, subFile.filename), func, rodataList, context)
        writeOtherRodata(args.split_functions, rodataList, context)

    if args.save_context is not None:
        head, tail = os.path.split(args.save_context)
        if head != "":
            os.makedirs(head, exist_ok=True)
        context.saveContextToFile(args.save_context)


if __name__ == "__main__":
    ovlDisassemblerMain()
