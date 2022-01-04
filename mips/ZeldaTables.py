#!/usr/bin/python3

from __future__ import annotations

from py_mips_disasm.mips.Utils import *
from py_mips_disasm.mips.MipsContext import Context


class DmaEntry:
    def __init__(self, vromStart: int, vromEnd: int, romStart: int, romEnd: int):
        self.vromStart: int = vromStart
        self.vromEnd: int = vromEnd
        self.romStart: int = romStart
        self.romEnd: int = romEnd


def getDmaAddresses(game: str, version: str) -> Dict[str, DmaEntry]:
    filetable = os.path.join(game, version, "tables", "dma_addresses.txt")
    table: Dict[str, DmaEntry] = dict()
    if os.path.exists(filetable):
        with open(filetable) as f:
            for line in f:
                filename, *data = line.strip().split(",")
                virtStart, virtEnd, physStart, physEnd = map(int, data)
                table[filename] = DmaEntry(virtStart, virtEnd, physStart, physEnd)
    return table


class OverlayTableEntry:
    def __init__(self, array_of_bytes: bytearray):
        wordsArray = bytesToBEWords(array_of_bytes)
        self.vromStart = wordsArray[0]
        self.vromEnd = wordsArray[1]
        self.vramStart = wordsArray[2]
        self.vramEnd = wordsArray[3]
        self.ramAddress = wordsArray[4]
        self.initVars = wordsArray[5]
        self.filenameAddres = wordsArray[6]
        self.allocationType = (wordsArray[7] > 16) & 0xFFFF
        self.instancesNum = (wordsArray[7] > 8) & 0xFF


def contextReadVariablesCsv(context: Context, game: str, version: str):
    variablesPath = os.path.join(game, version, "tables", f"variables_{game}_{version}.csv")
    if os.path.exists(variablesPath):
        context.readVariablesCsv(variablesPath)

def contextReadFunctionsCsv(context: Context, game: str, version: str):
    functionsPath = os.path.join(game, version, "tables", f"functions_{game}_{version}.csv")
    if os.path.exists(functionsPath):
        context.readFunctionsCsv(functionsPath)
