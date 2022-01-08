#!/usr/bin/python3

from __future__ import annotations

from py_mips_disasm.mips.Utils import *
from py_mips_disasm.mips.GlobalConfig import GlobalConfig

from py_mips_disasm.mips.MipsText import Text
from py_mips_disasm.mips.MipsData import Data
from py_mips_disasm.mips.MipsRodata import Rodata
from py_mips_disasm.mips.MipsBss import Bss
from py_mips_disasm.mips.MipsContext import Context
from py_mips_disasm.mips.FileSplitFormat import FileSplitFormat, FileSectionType

from .MipsFileGeneric import FileGeneric


class FileSplits(FileGeneric):
    def __init__(self, array_of_bytes: bytearray, filename: str, version: str, context: Context, game: str, splitsData: FileSplitFormat | None = None):
        super().__init__(array_of_bytes, filename, version, context, game)

        if splitsData is None:
            self.textList[filename] = Text(self.bytes, filename, version, context)
        else:
            for offset, vram, sub_fileName, section, nextOffset, isHandwritten in splitsData:
                if self.vRamStart <= 0:
                    self.vRamStart = vram

                # print("\t", offset, vram, sub_fileName, section, nextOffset, isHandwritten)

                if section == FileSectionType.Text:
                    f = Text(self.bytes[offset:nextOffset], sub_fileName, version, context)

                    f.parent = self
                    f.offset = offset
                    f.vRamStart = self.vRamStart
                    f.isHandwritten = isHandwritten

                    self.textList[sub_fileName] = f
                elif section == FileSectionType.Data:
                    f = Data(self.bytes[offset:nextOffset], sub_fileName, version, context)

                    f.parent = self
                    f.offset = offset
                    f.vRamStart = self.vRamStart
                    f.isHandwritten = isHandwritten

                    self.dataList[sub_fileName] = f
                elif section == FileSectionType.Rodata:
                    f = Rodata(self.bytes[offset:nextOffset], sub_fileName, version, context)

                    f.parent = self
                    f.offset = offset
                    f.vRamStart = self.vRamStart
                    f.isHandwritten = isHandwritten

                    self.rodataList[sub_fileName] = f
                elif section == FileSectionType.Bss:
                    f = Bss(vram, vram + (nextOffset - offset), sub_fileName, version, context)

                    f.parent = self
                    f.offset = offset
                    f.vRamStart = self.vRamStart
                    f.isHandwritten = isHandwritten

                    self.bssList[sub_fileName] = f
                else:
                    eprint("Error! Section not set!")
                    exit(1)


