#! /usr/bin/env python3

from __future__ import annotations

import argparse
import os
from pathlib import Path

import spimdisasm

from mips.ZeldaTables import getFileAddresses

def writeFiles(ovlSection: spimdisasm.mips.FileSplits, textOutput: str, dataOutput: str|None):
    spimdisasm.common.Utils.printVerbose("Writing files...")

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

    for subFileName, section in ovlSection.sectionsDict[spimdisasm.common.FileSectionType.Text].items():
        section.saveToFile(os.path.join(textOutput, subFileName))

    for sectionType, filesinSection in ovlSection.sectionsDict.items():
        if sectionType == spimdisasm.common.FileSectionType.Text:
            continue
        for subFileName, section in filesinSection.items():
            section.saveToFile(os.path.join(dataOutput, subFileName))


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

    spimdisasm.common.Context.addParametersToArgParse(parser)

    spimdisasm.common.GlobalConfig.addParametersToArgParse(parser)

    parser.add_argument("--add-filename", help="Adds the filename of the file to the generated function/variable name")

    args = parser.parse_args()

    spimdisasm.common.GlobalConfig.parseArgs(args)

    spimdisasm.common.GlobalConfig.REMOVE_POINTERS = args.nuke_pointers
    spimdisasm.common.GlobalConfig.IGNORE_BRANCHES = args.nuke_pointers
    if args.nuke_pointers:
        spimdisasm.common.GlobalConfig.IGNORE_WORD_LIST.add(0x80)

    spimdisasm.common.GlobalConfig.PRODUCE_SYMBOLS_PLUS_OFFSET = True
    spimdisasm.common.GlobalConfig.TRUST_USER_FUNCTIONS = True


    context = spimdisasm.common.Context()
    context.parseArgs(args)

    array_of_bytes = spimdisasm.common.Utils.readFileAsBytearray(args.binary)
    input_name = os.path.splitext(os.path.split(args.binary)[1])[0]


    splitsData = None
    if args.file_splits is not None and os.path.exists(args.file_splits):
        splitsData = spimdisasm.common.FileSplitFormat()
        splitsData.readCsvFile(args.file_splits)

    fileAddresses = getFileAddresses(args.file_addresses)

    if args.reloc_separate:
        reloc_filename = findRelocFile(input_name, args.file_addresses)
        relocPath = Path(args.binary).parent / reloc_filename

        reloc_array_of_bytes = spimdisasm.common.Utils.readFileAsBytearray(relocPath)

        relocSection = spimdisasm.mips.sections.SectionRelocZ64(context, 0, len(reloc_array_of_bytes), 0, reloc_filename, reloc_array_of_bytes, 0, "reloc")
        relocSection.differentSegment = True
        if reloc_filename in fileAddresses:
            relocSection.setVram(fileAddresses[reloc_filename].vramStart)
    else:
        relocSection = spimdisasm.mips.sections.SectionRelocZ64(context, 0, len(array_of_bytes), 0, input_name, array_of_bytes, 0, None)
        relocSection.differentSegment = False


    vramStart = -1
    if input_name in fileAddresses:
        vramStart = fileAddresses[input_name].vramStart

    f = spimdisasm.mips.FileSplits(context, 0, len(array_of_bytes), vramStart, input_name, array_of_bytes, 0, None, splitsData=splitsData, relocSection=relocSection)

    f.analyze()

    if spimdisasm.common.GlobalConfig.VERBOSE:
        for sectDict in f.sectionsDict.values():
            for section in sectDict.values():
                section.printAnalyzisResults()

    if args.nuke_pointers:
        spimdisasm.common.Utils.printVerbose("Nuking pointers...")
        f.removePointers()

    writeFiles(f, args.output, args.data_output)

    if args.split_functions is not None:
        spimdisasm.common.Utils.printVerbose("Spliting functions")
        rodataList: list[spimdisasm.mips.sections.SectionRodata] = list()

        splitFunctionsPath = Path(args.split_functions)

        for rodataName, rodataSection in f.sectionsDict[spimdisasm.common.FileSectionType.Rodata].items():
            assert(isinstance(rodataSection, spimdisasm.mips.sections.SectionRodata))
            rodataList.append(rodataSection)

        for path, subFile in f.sectionsDict[spimdisasm.common.FileSectionType.Text].items():
            assert(isinstance(subFile, spimdisasm.mips.sections.SectionText))
            for func in subFile.symbolList:
                assert isinstance(func, spimdisasm.mips.symbols.SymbolFunction)

                spimdisasm.mips.FilesHandlers.writeSplitedFunction(splitFunctionsPath / subFile.name, func, rodataList)
        spimdisasm.mips.FilesHandlers.writeOtherRodata(splitFunctionsPath, rodataList)

    if args.save_context is not None:
        contextPath = Path(args.save_context)
        contextPath.parent.mkdir(parents=True, exist_ok=True)
        context.saveContextToFile(contextPath)


if __name__ == "__main__":
    ovlDisassemblerMain()
