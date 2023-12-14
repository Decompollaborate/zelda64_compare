#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import spimdisasm


class SplitEntry:
    def __init__(self, version: str, filename: str, offset: int, size: int = -1, vram: int = -1):
        self.version: str = version
        self.filename: str = filename
        self.offset: int = offset
        self.size: int = size
        self.vram: int = vram
        self.section: str = ""

    def __str__(self) -> str:
        out = "<SplitData "

        out += f"{self.version}/{self.filename} Offset: 0x{self.offset:X}"

        if self.section != "":
            out += f" Section: {self.section}"
        if self.size >= 0:
            out += f" Size: 0x{self.size:X}"
        if self.vram >= 0:
            out += f" VRAM: 0x{self.vram:X}"

        return out + ">"

    def __repr__(self) -> str:
        return self.__str__()

    def splatSection(self) -> str:
        if self.section == ".text":
            return "asm"
        if self.section.startswith("."):
            return self.section[1:]
        return "data"


def readSplitsFromCsv(csvfilename: Path) -> dict[str, dict[str, list[SplitEntry]]]:
    code_splits_file = spimdisasm.common.Utils.readCsv(csvfilename)

    columnsPerVersion = 3
    if code_splits_file[0][2] != "":
        try:
            columnsPerVersion = int(code_splits_file[0][2])
        except:
            pass

    header = code_splits_file[0][3::columnsPerVersion]
    splits: dict[str, dict[str, list[SplitEntry]]] = { h: dict() for h in header }

    for row_num in range(2, len(code_splits_file)):
        row = code_splits_file[row_num]
        if len(row) == 0:
            # row had a comment at the begninning
            continue

        try:
            filename1, filename2, _, *data = row

            name = filename1 or filename2
            if name == "":
                continue

            for column_set_num in range(len(header)):
                h = header[column_set_num]
                if h == "":
                    continue
                subrow = data[ column_set_num * columnsPerVersion : (column_set_num + 1) * columnsPerVersion ]
                offset = subrow[0]
                vram = subrow[1]
                size = subrow[2]

                try:
                    offset = int(offset, 16)
                except:
                    continue

                try:
                    size = int(size, 16)
                except:
                    size = -1

                try:
                    vram = int(vram, 16)
                except:
                    vram = -1

                if name not in splits[h]:
                    splits[h][name] = list()

                splits[h][name].append(SplitEntry(h, name, offset, size, vram))
        except:
            spimdisasm.common.Utils.eprint(f"error when parsing {str(csvfilename)}, line {row_num+1}: could not read row:")
            spimdisasm.common.Utils.eprint(f"    {row}\n")
            raise
    return splits

def getFileStartsFromEntries(splits: dict[str, SplitEntry], fileEndOffset: int) -> list[tuple[int, int, str]]:
    starts = list()
    for filename, entry in splits.items():
        starts.append((entry.offset, entry.size, filename))
    starts.append((fileEndOffset, 0, "end"))

    starts.sort()

    i = 0
    while i < len(starts) - 1:
        start, size, filename = starts[i]
        nextStart, _, _ = starts[i+1]

        end = start + size
        if size < 0:
            end = nextStart
            starts[i] = (start, nextStart-start, filename)

        if end < nextStart:
            starts.insert(i+1, (end, -1, f"file_{end:06X}"))

        i += 1

    return starts


def readSegmentSplitsFromSheetCsv(csvList: list[tuple[str, Path]]) -> dict[str, list[SplitEntry]]:
    tablePerVersion: dict[str, list[SplitEntry]] = dict()

    for section, csvPath in csvList:
        oldSection = section
        if not csvPath.exists():
            continue

        splits = readSplitsFromCsv(csvPath)

        for version, filesDict in splits.items():
            if version == "":
                continue

            if version not in tablePerVersion:
                tablePerVersion[version] = []

            auxList: list[SplitEntry] = []

            for filename, splitDataList in filesDict.items():
                section = oldSection
                for splitData in splitDataList:
                    if splitData.filename.startswith(".") and splitData.filename != ".end":
                        section = splitData.filename
                        continue
                    splitData.section = section
                    if splitData.offset < 0 or splitData.vram < 0 or splitData.filename == "":
                        continue
                    auxList.append(splitData)

            if len(auxList) == 0:
                continue

            # fake extra to avoid problems
            auxList.append(SplitEntry(version, "end", 0xFFFFFF, 0, 0x80FFFFFF))

            # Reading from the file may not be sorted by offset
            auxList.sort(key=lambda x: x.offset)

            i = 0
            while i < len(auxList) - 1:
                currentSplit = auxList[i]
                nextSplit = auxList[i+1]

                end = currentSplit.offset + currentSplit.size
                if currentSplit.size <= 0:
                    end = nextSplit.offset

                if end < nextSplit.offset:
                    # Adds placeholder files
                    placeholderSplit = SplitEntry(version, f"file_{end:06X}", end, -1, currentSplit.vram + (end - currentSplit.offset))
                    placeholderSplit.section = currentSplit.section
                    auxList.insert(i+1, placeholderSplit)
                    end = nextSplit.offset

                entry = SplitEntry(version, currentSplit.filename, currentSplit.offset, end - currentSplit.offset, currentSplit.vram)
                entry.section = currentSplit.section
                tablePerVersion[version].append(entry)

                i += 1


    for version, splitsList in tablePerVersion.items():
        splitsList.sort(key=lambda x: x.offset)

        i = 0
        while i < len(splitsList)-1:
            currentSplit = splitsList[i]
            nextSplit = splitsList[i+1]

            # Looks for duplicates on section changes
            if currentSplit.section != nextSplit.section:
                if currentSplit.offset == nextSplit.offset:
                    del splitsList[i]
                    continue
            i += 1

    return tablePerVersion
