#!/usr/bin/python3

from __future__ import annotations

from py_mips_disasm.mips.Utils import *
from py_mips_disasm.mips.GlobalConfig import GlobalConfig

from py_mips_disasm.mips.MipsText import Text
from py_mips_disasm.mips.MipsContext import Context
from py_mips_disasm.mips.FileSplitFormat import FileSplitFormat, FileSectionType
from py_mips_disasm.mips.FilesHandlers import createSectionFromSplitEntry

from .MipsFileGeneric import FileGeneric


class FileSplits(FileGeneric):
    def __init__(self, array_of_bytes: bytearray, filename: str, version: str, context: Context, game: str, splitsData: FileSplitFormat | None = None):
        super().__init__(array_of_bytes, filename, version, context, game)

        if splitsData is None:
            self.sectionsDict[FileSectionType.Text][filename] = Text(self.bytes, filename, version, context)
        else:
            for splitEntry in splitsData:
                if self.vRamStart <= 0:
                    self.vRamStart = splitEntry.vram

                f = createSectionFromSplitEntry(splitEntry, self.bytes, splitEntry.fileName, context)
                f.parent = self

                self.sectionsDict[splitEntry.section][splitEntry.fileName] = f
