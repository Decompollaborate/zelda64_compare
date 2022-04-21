#!/usr/bin/env python3

from __future__ import annotations

from py_mips_disasm.backend.common.GlobalConfig import GlobalConfig
from py_mips_disasm.backend.common.Context import Context
from py_mips_disasm.backend.common.FileSectionType import FileSectionType
from py_mips_disasm.backend.common.FileSplitFormat import FileSplitFormat

from py_mips_disasm.backend.mips.MipsText import Text
from py_mips_disasm.backend.mips.FilesHandlers import createSectionFromSplitEntry

from .MipsFileGeneric import FileGeneric


class FileSplits(FileGeneric):
    def __init__(self, array_of_bytes: bytearray, filename: str, context: Context, splitsData: FileSplitFormat | None = None):
        super().__init__(array_of_bytes, filename, context)

        if splitsData is None:
            self.sectionsDict[FileSectionType.Text][filename] = Text(self.bytes, filename, context)
        else:
            for splitEntry in splitsData:
                if self.vRamStart < 0:
                    self.vRamStart = splitEntry.vram

                f = createSectionFromSplitEntry(splitEntry, self.bytes, splitEntry.fileName, context)
                f.parent = self
                f.setCommentOffset(splitEntry.offset)

                self.sectionsDict[splitEntry.section][splitEntry.fileName] = f
