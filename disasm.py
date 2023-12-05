#! /usr/bin/env python3

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import sys

import spimdisasm
from spimdisasm import frontendCommon as fec

from mips.ZeldaTables import getFileAddressList

def baseromPath(game: str, version: str, filename: str) -> Path:
    return Path(game, version, "baserom", filename)

def tablePath(game: str, version: str, table: str) -> Path:
    return Path(os.path.join(game, version, "tables", table))

def outputPath(game: str, version: str, output: str) -> Path:
    return Path(os.path.join(game, version, "asm", output))

@dataclass
class Split:
    section: spimdisasm.mips.sections.SectionBase
    outputPath: Path

def loadStaticFile(context: spimdisasm.common.Context, game: str, version: str, filename: str) -> list[Split]:
    inputPath = baseromPath(game, version, filename)
    array_of_bytes = spimdisasm.common.Utils.readFileAsBytearray(inputPath)

    splits = spimdisasm.singleFileDisasm.getSplits(tablePath(game, version, f"files_{filename}.csv"), 0, len(array_of_bytes), 0, None, None, False)

    outputDir = outputPath(game, version, filename)
    processedFiles, processedFilesOutputPaths = fec.FrontendUtilities.getSplittedSections(context, splits, array_of_bytes, inputPath, outputDir, outputDir)

    splits = []
    for sectionType, filesInSection in sorted(processedFiles.items()):
        pathLists = processedFilesOutputPaths[sectionType]
        for f, path in zip(filesInSection, pathLists):
            if f.name == '[PADDING]':
                continue
            splits.append(Split(f, path))
    return splits

def loadOverlay(context: spimdisasm.common.Context, game: str, version: str, filename: str, vramStart: int, relocFilename: str|None) -> Split:
    inputPath = baseromPath(game, version, filename)
    array_of_bytes = spimdisasm.common.Utils.readFileAsBytearray(inputPath)

    splitsPath = tablePath(game, version, f"files_{filename}.csv")
    if splitsPath.exists():
        splitsData = spimdisasm.common.FileSplitFormat()
        splitsData.readCsvFile(splitsPath)
    else:
        splitsData = None

    if relocFilename is not None:
        relocPath = baseromPath(game, version, relocFilename)
        reloc_array_of_bytes = spimdisasm.common.Utils.readFileAsBytearray(relocPath)

        relocSection = spimdisasm.mips.sections.SectionRelocZ64(context, 0, len(reloc_array_of_bytes), 0, relocFilename, reloc_array_of_bytes, 0, "reloc")
        relocSection.differentSegment = True
        relocSection.setVram(vramStart)
    elif splitsData is None:
        relocSection = spimdisasm.mips.sections.SectionRelocZ64(context, 0, len(array_of_bytes), 0, inputPath.stem, array_of_bytes, 0, None)
        relocSection.differentSegment = False
    else:
        relocSection = None

    outputDir = outputPath(game, version, filename)
    ovlSection = spimdisasm.mips.FileSplits(context, 0, len(array_of_bytes), vramStart, inputPath.stem, array_of_bytes, 0, None, splitsData=splitsData, relocSection=relocSection)

    splits = []
    for sectionType, filesInSection in ovlSection.sectionsDict.items():
       for subFileName, section in filesInSection.items():
            splits.append(Split(section, outputDir / subFileName))
    return splits

def main() -> int:
    parser = argparse.ArgumentParser(description="Disassemble boot, code, and overlays.")
    parser.add_argument("--game", help="Game to use.", required=True)
    parser.add_argument("--version", help="Version to use.", required=True)
    parser.add_argument("-r", "--reloc-separate", help="Should look for separate relocation file", action="store_true")

    spimdisasm.common.Context.addParametersToArgParse(parser)
    spimdisasm.common.GlobalConfig.addParametersToArgParse(parser)
    spimdisasm.mips.InstructionConfig.addParametersToArgParse(parser)

    args = parser.parse_args()
    game = args.game
    version = args.version

    context = spimdisasm.common.Context()
    context.parseArgs(args)
    context.changeGlobalSegmentRanges(0x00000000, 0x01000000, 0x8000000, 0x81000000)

    spimdisasm.mips.InstructionConfig.parseArgs(args)
    spimdisasm.common.GlobalConfig.parseArgs(args)

    spimdisasm.common.GlobalConfig.PRODUCE_SYMBOLS_PLUS_OFFSET = True
    spimdisasm.common.GlobalConfig.TRUST_USER_FUNCTIONS = True

    splits = []
    for filename in ["boot", "code"]:
        splits.extend(loadStaticFile(context, game, version, filename))

    fileAddresses = getFileAddressList(Path(tablePath(game, version, "file_addresses.csv")))

    i = 0
    while i < len(fileAddresses):
        entry = fileAddresses[i]
        i += 1
        if entry.filename.startswith("ovl_"):
            if args.reloc_separate:
                # relocation file is always the next entry
                relocFilename = fileAddresses[i].filename
                i += 1
            else:
                relocFilename = None
            splits.extend(loadOverlay(context, game, version, entry.filename, entry.vramStart, relocFilename))

    # analyze .text first to generate data symbols
    splits.sort(key=lambda split: split.section.sectionType)

    for split in splits:
        spimdisasm.common.Utils.printQuietless(f"Analyzing {split.outputPath}{split.section.sectionType.toStr()} ...")
        split.section.analyze()

    for split in splits:
        spimdisasm.common.Utils.printQuietless(f"Writing {split.outputPath}{split.section.sectionType.toStr()} ...")
        split.outputPath.parent.mkdir(parents=True, exist_ok=True)
        split.section.saveToFile(str(split.outputPath))

    return 0


if __name__ == "__main__":
    sys.exit(main())
