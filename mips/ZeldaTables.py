#!/usr/bin/env python3

from __future__ import annotations

import os
from typing import Dict
from py_mips_disasm.backend.common.Context import Context


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


def getFileAddresses(filePath: str | None) -> Dict[str, FileAddressesEntry]:
    table: Dict[str, FileAddressesEntry] = dict()
    if filePath is not None and os.path.exists(filePath):
        with open(filePath) as f:
            header = True
            for line in f:
                if header:
                    # Skip csv header
                    header = False
                    continue
                filename, *data = line.strip().split(",")
                table[filename] = FileAddressesEntry(filename, *data)
    return table


def contextReadVariablesCsv(context: Context, game: str, version: str):
    variablesPath = os.path.join(game, version, "tables", f"variables.csv")
    if os.path.exists(variablesPath):
        context.readVariablesCsv(variablesPath)

def contextReadFunctionsCsv(context: Context, game: str, version: str):
    functionsPath = os.path.join(game, version, "tables", f"functions.csv")
    if os.path.exists(functionsPath):
        context.readFunctionsCsv(functionsPath)
