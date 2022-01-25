#!/usr/bin/python3

from __future__ import annotations

from py_mips_disasm.mips.Utils import *
from py_mips_disasm.mips.GlobalConfig import GlobalConfig

from py_mips_disasm.mips.MipsFileBase import FileBase
from py_mips_disasm.mips.MipsText import Text
from py_mips_disasm.mips.MipsData import Data
from py_mips_disasm.mips.MipsRodata import Rodata
from py_mips_disasm.mips.MipsBss import Bss
from py_mips_disasm.mips.MipsContext import Context
from py_mips_disasm.mips.FileSplitFormat import FileSplitFormat, FileSectionType, FileSplitEntry
from py_mips_disasm.mips.FilesHandlers import createSectionFromSplitEntry

from .MipsReloc import Reloc
from .MipsFileGeneric import FileGeneric

from .ZeldaTables import OverlayTableEntry


class FileOverlay(FileGeneric):
    def __init__(self, array_of_bytes: bytearray, filename: str, context: Context, tableEntry: OverlayTableEntry=None, splitsData: FileSplitFormat | None = None, vramStartParam: int = -1):
        super().__init__(array_of_bytes, filename, context)

        self.vRamStart = vramStartParam

        self.initVarsAddress = -1
        if tableEntry is not None:
            self.vRamStart = tableEntry.vramStart
            self.initVarsAddress = tableEntry.initVars

        for subfileVram, subfileData in context.files.items():
            if filename == subfileData.name:
                self.vRamStart = subfileVram
                break


        seekup = self.words[-1]
        headerBPos = self.size - seekup
        headerWPos = headerBPos//4

        text_size = self.words[headerWPos]
        data_size = self.words[headerWPos+1]
        rodata_size = self.words[headerWPos+2]
        bss_size = self.words[headerWPos+3]
        reloc_size = 4*5 + 4*self.words[headerWPos+4]

        self.splitsDataList: List[FileSplitEntry] = []
        if splitsData is not None and len(splitsData) > 0:
            for splitEntry in splitsData:
                self.splitsDataList.append(splitEntry)
        else:
            vram = self.vRamStart

            start = 0
            end = text_size
            if self.vRamStart > 0:
                vram = self.vRamStart + start
            splitEntry = FileSplitEntry(start, vram, filename, FileSectionType.Text, end, False, False)
            self.splitsDataList.append(splitEntry)

            start += text_size
            end += data_size
            if self.vRamStart > 0:
                vram = self.vRamStart + start
            splitEntry = FileSplitEntry(start, vram, filename, FileSectionType.Data, end, False, False)
            self.splitsDataList.append(splitEntry)

            start += data_size
            end += rodata_size
            if self.vRamStart > 0:
                vram = self.vRamStart + start
            splitEntry = FileSplitEntry(start, vram, filename, FileSectionType.Rodata, end, False, False)
            self.splitsDataList.append(splitEntry)

            start += rodata_size
            end += bss_size
            if self.vRamStart > 0:
                vram = self.vRamStart + start
            splitEntry = FileSplitEntry(start, vram, filename, FileSectionType.Bss, end, False, False)
            self.splitsDataList.append(splitEntry)


        for splitEntry in self.splitsDataList:
            if self.vRamStart <= 0:
                self.vRamStart = splitEntry.vram

            f = createSectionFromSplitEntry(splitEntry, self.bytes, splitEntry.fileName, context)
            f.parent = self
            f.setCommentOffset(splitEntry.offset)

            self.sectionsDict[splitEntry.section][splitEntry.fileName] = f


        relocStart = text_size + data_size + rodata_size
        self.reloc = Reloc(self.bytes[relocStart:], filename, context)
        self.reloc.parent = self
        self.reloc.vRamStart = self.vRamStart
        if self.vRamStart >= 0:
            self.reloc.vRamStart = self.vRamStart + relocStart
        self.reloc.setCommentOffset(relocStart)


    def setVRamStart(self, vRamStart: int):
        super().setVRamStart(vRamStart)
        self.reloc.vRamStart = vRamStart

    def getHash(self) -> str:
        bytes = bytearray(0)
        for sectDict in self.sectionsDict.values():
            for section in sectDict.values():
                bytes += section.bytes
        bytes += self.reloc.bytes
        return getStrHash(bytes)

    def analyze(self):
        for entry in self.reloc.entries:
            section = entry.getSectionName()
            # type_name = entry.getTypeName()
            offset = entry.offset
            if entry.reloc == 0:
                continue
            if section == ".text":
                for subFile in self.sectionsDict[FileSectionType.Text].values():
                    subFile.pointersOffsets.append(offset)
            elif section == ".data":
                for subFile in self.sectionsDict[FileSectionType.Data].values():
                    subFile.pointersOffsets.append(offset)
            elif section == ".rodata":
                for subFile in self.sectionsDict[FileSectionType.Rodata].values():
                    subFile.pointersOffsets.append(offset)
            elif section == ".bss":
                for subFile in self.sectionsDict[FileSectionType.Bss].values():
                    subFile.pointersOffsets.append(offset)

        # self.sectionsDict[FileSectionType.Text][self.filename].removeTrailingNops()

        super().analyze()
        self.reloc.analyze()


    def compareToFile(self, other_file: FileBase):
        result = super().compareToFile(other_file)

        if isinstance(other_file, FileOverlay):
            result["filesections"]["reloc"] = {self.reloc.filename: self.reloc.compareToFile(other_file.reloc)}

        return result

    def blankOutDifferences(self, other_file: FileBase) -> bool:
        if not GlobalConfig.REMOVE_POINTERS:
            return False

        was_updated = super().blankOutDifferences(other_file)
        if isinstance(other_file, FileOverlay):
            was_updated = self.reloc.blankOutDifferences(other_file.reloc) or was_updated

        return was_updated

    def removePointers(self) -> bool:
        if not GlobalConfig.REMOVE_POINTERS:
            return False

        """
        for entry in self.reloc.entries:
            section = entry.getSectionName()
            type_name = entry.getTypeName()
            offset = entry.offset//4
            if entry.reloc == 0:
                continue
            if section == ".text":
                for func in self.text.functions[::-1]:
                    if entry.offset >= func.inFileOffset:
                        offset = (entry.offset- func.inFileOffset)//4
                        instr = func.instructions[offset]
                        if type_name == "R_MIPS_26":
                            func.instructions[offset] = wordToInstruction(instr.instr & 0xFC000000)
                        elif type_name in ("R_MIPS_HI16", "R_MIPS_LO16"):
                            func.instructions[offset] = wordToInstruction(instr.instr & 0xFFFF0000)
                        else:
                            raise RuntimeError(f"Invalid <{type_name}> in .text of file '{self.version}/{self.filename}'. Reloc: {entry}")
                        break
            elif section == ".data":
                word = self.data.words[offset]
                if type_name == "R_MIPS_32":
                    self.data.words[offset] = word & 0xFF000000
                elif type_name == "R_MIPS_26":
                    self.data.words[offset] = word & 0xFC000000
                elif type_name in ("R_MIPS_HI16", "R_MIPS_LO16"):
                    self.data.words[offset] = word & 0xFFFF0000
                else:
                    raise RuntimeError(f"Invalid <{type_name}> in .data of file '{self.version}/{self.filename}'. Reloc: {entry}")
            elif section == ".rodata":
                word = self.rodata.words[offset]
                if type_name == "R_MIPS_32":
                    self.rodata.words[offset] = word & 0xFF000000
                elif type_name == "R_MIPS_26":
                    self.rodata.words[offset] = word & 0xFC000000
                elif type_name in ("R_MIPS_HI16", "R_MIPS_LO16"):
                    self.rodata.words[offset] = word & 0xFFFF0000
                else:
                    raise RuntimeError(f"Invalid <{type_name}> in .rodata of file '{self.version}/{self.filename}'. Reloc: {entry}")
            elif section == ".bss":
                word = self.bss.words[offset]
                if type_name == "R_MIPS_32":
                    self.bss.words[offset] = word & 0xFF000000
                elif type_name == "R_MIPS_26":
                    self.bss.words[offset] = word & 0xFC000000
                elif type_name in ("R_MIPS_HI16", "R_MIPS_LO16"):
                    self.bss.words[offset] = word & 0xFFFF0000
                else:
                    raise RuntimeError(f"Invalid <{type_name}> in .bss of file '{self.version}/{self.filename}'. Reloc: {entry}")
            else:
                pass
                #raise RuntimeError(f"Invalid reloc section <{section}> in file '{self.version}/{self.filename}'. Reloc: {entry}")
        """

        was_updated = self.reloc.nRelocs >= 0
        was_updated = super().removePointers() or was_updated
        was_updated = self.reloc.removePointers() or was_updated

        return was_updated

    def updateBytes(self):
        super().updateBytes()
        self.reloc.updateBytes()

    def saveToFile(self, filepath: str):
        super().saveToFile(filepath)

        self.reloc.saveToFile(filepath + self.reloc.filename)

    def updateCommentOffset(self):
        for sectDict in self.sectionsDict.values():
            for section in sectDict.values():
                section.setCommentOffset(section.commentOffset)
