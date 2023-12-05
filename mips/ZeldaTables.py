#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import spimdisasm


class FileAddressesEntry:
    def __init__(self, filename, vromStart, vromEnd, romStart, romEnd, sizeVrom, compressed, vramStart, vramEnd, sizeVram, bss, type, number, *discard):
        self.filename = filename

        self.vromStart = int(vromStart, 16)
        self.vromEnd = int(vromEnd, 16)
        self.romStart = int(romStart, 16)
        self.romEnd = int(romEnd, 16)

        self.sizeVrom = int(sizeVrom, 16)

        self.compressed = compressed == "Y"

        self.vramStart = -1
        if vramStart != "":
            self.vramStart = int(vramStart, 16)
        self.vramEnd = -1
        if vramEnd != "":
            self.vramEnd = int(vramEnd, 16)
        self.sizeVram = -1
        if sizeVram != "":
            self.sizeVram = int(sizeVram, 16)

        self.bss = bss
        self.type = type
        self.number = number




def getFileAddressList(filePath: Path | None) -> list[FileAddressesEntry]:
    result: list[FileAddressesEntry] = []
    if filePath is not None and filePath.exists():
        with filePath.open() as f:
            header = True
            for line in f:
                if header:
                    # Skip csv header
                    header = False
                    continue
                filename, *data = line.strip().split(",")
                result.append(FileAddressesEntry(filename, *data))
    return result

def getFileAddresses(filePath: Path | None) -> dict[str, FileAddressesEntry]:
    return {entry.filename: entry for entry in getFileAddressList(filePath)}


def contextReadVariablesCsv(context: spimdisasm.common.Context, game: str, version: str):
    variablesPath = Path(game, version, "tables", "variables.csv")
    if variablesPath.exists():
        context.globalSegment.readVariablesCsv(variablesPath)

def contextReadFunctionsCsv(context: spimdisasm.common.Context, game: str, version: str):
    functionsPath = Path(game, version, "tables", "functions.csv")
    if functionsPath.exists():
        context.globalSegment.readFunctionsCsv(functionsPath)
