#!/usr/bin/env python3

from __future__ import annotations

from typing import Dict, List, Tuple
import py_mips_disasm.backend.common.Utils as disasm_Utils


class SplitEntry:
    def __init__(self, version: str, filename: str, offset: int, size: int = -1, vram: int = -1):
        self.version: str = version
        self.filename: str = filename
        self.offset: int = offset
        self.size: int = size
        self.vram: int = vram

    def __str__(self) -> str:
        out = "<SplitData "

        out += f"{self.version}/{self.filename} Offset: 0x{self.offset:X}"

        if self.size >= 0:
            out += f" Size: 0x{self.size:X}"
        if self.vram >= 0:
            out += f" VRAM: 0x{self.vram:X}"

        return out + ">"

    def __repr__(self) -> str:
        return self.__str__()


def readSplitsFromCsv(csvfilename: str) -> Dict[str, Dict[str, List[SplitEntry]]]:
    code_splits_file = disasm_Utils.readCsv(csvfilename)

    columnsPerVersion = 3
    if code_splits_file[0][2] != "":
        try:
            columnsPerVersion = int(code_splits_file[0][2])
        except:
            pass

    header = code_splits_file[0][3::columnsPerVersion]
    splits: Dict[str, Dict[str, List[SplitEntry]]] = { h: dict() for h in header }

    for row_num in range(2, len(code_splits_file)):
        row = code_splits_file[row_num]
        filename1, filename2, _, *data = row

        name = filename1 or filename2
        if name == "":
            continue

        for column_set_num in range(len(header)):
            h = header[column_set_num]
            if h == "":
                continue
            try:
                subrow = data[ column_set_num * columnsPerVersion : (column_set_num + 1) * columnsPerVersion ]
                offset = subrow[0]
                vram = subrow[1]
                size = subrow[2]
            except:
                print("error when parsing {}, line {}: could not read row:".format(csvfilename, row_num))
                print("    {}\n".format(row))
                raise

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
    return splits

def getFileStartsFromEntries(splits: Dict[str, SplitEntry], fileEndOffset: int) -> List[Tuple[int, int, str]]:
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
            starts.insert(i+1, (end, -1, f"file_{disasm_Utils.toHex(end, 6)}"))

        i += 1

    return starts
