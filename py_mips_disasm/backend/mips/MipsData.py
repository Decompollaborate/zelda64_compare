#!/usr/bin/env python3

from __future__ import annotations

from ..common.Utils import *
from ..common.GlobalConfig import GlobalConfig
from ..common.FileSectionType import FileSectionType

from .MipsSection import Section


class Data(Section):
    def analyze(self):
        if self.vRamStart > -1:
            offset = 0
            for w in self.words:
                currentVram = self.getVramOffset(offset)

                contextSymbol = self.context.getSymbol(currentVram, tryPlusOffset=False)
                if contextSymbol is not None:
                    contextSymbol.isDefined = True

                if w >= self.vRamStart and w < 0x84000000:
                    if self.context.getAnySymbol(w) is None:
                        self.context.newPointersInData.add(w)

                offset += 4


    def removePointers(self) -> bool:
        if not GlobalConfig.REMOVE_POINTERS:
            return False

        was_updated = False
        for i in range(self.sizew):
            top_byte = (self.words[i] >> 24) & 0xFF
            if top_byte == 0x80:
                self.words[i] = top_byte << 24
                was_updated = True
            if (top_byte & 0xF0) == 0x00 and (top_byte & 0x0F) != 0x00:
                self.words[i] = top_byte << 24
                was_updated = True

        return was_updated


    def disassembleToFile(self, f: TextIO):
        f.write(".include \"macro.inc\"\n")
        f.write("\n")
        f.write("# assembler directives\n")
        f.write(".set noat      # allow manual use of $at\n")
        f.write(".set noreorder # don't insert nops after branches\n")
        f.write(".set gp=64     # allow use of 64-bit general purpose registers\n")
        f.write("\n")
        f.write(".section .data\n")
        f.write("\n")
        f.write(".balign 16\n")

        offset = 0
        inFileOffset = self.offset
        i = 0
        while i < self.sizew:
            w = self.words[i]
            label = ""

            # try to get the symbol name from the offset of the file (possibly from a .o elf file)
            possibleSymbolName = self.context.getOffsetSymbol(inFileOffset, FileSectionType.Data)
            if possibleSymbolName is not None:
                if possibleSymbolName.isStatic:
                    label = "\n/* static variable */"
                label += f"\nglabel {possibleSymbolName.name}\n"

            # if we have vram available, try to get the symbol name from the Context
            if self.vRamStart > -1:
                currentVram = self.getVramOffset(offset)

                label = self.getSymbolLabelAtVram(currentVram, label)

                contVariable = self.context.getSymbol(currentVram, False)
                if contVariable is not None:
                    contVariable.isDefined = True

            value = toHex(w, 8)
            possibleReference = self.context.getRelocSymbol(inFileOffset, FileSectionType.Data)
            if possibleReference is not None:
                value = possibleReference.getNamePlusOffset(w)

            symbol = self.context.getAnySymbol(w)
            if symbol is not None:
                value = symbol.name

            comment = self.generateAsmLineComment(offset)
            line = f"{label}{comment} .word {value}"
            f.write(line + "\n")
            i += 1
            offset += 4
            inFileOffset += 4

    def saveToFile(self, filepath: str):
        super().saveToFile(filepath + ".data")

        if self.size == 0:
            return

        if filepath == "-":
            self.disassembleToFile(sys.stdout)
        else:
            with open(filepath + ".data.s", "w") as f:
                self.disassembleToFile(f)
