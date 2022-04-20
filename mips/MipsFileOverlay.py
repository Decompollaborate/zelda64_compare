#!/usr/bin/env python3

from __future__ import annotations

from typing import List
import py_mips_disasm.backend.common.Utils as disasm_Utils
from py_mips_disasm.backend.common.GlobalConfig import GlobalConfig
from py_mips_disasm.backend.common.Context import Context
from py_mips_disasm.backend.common.FileSectionType import FileSectionType, FileSections_ListBasic
from py_mips_disasm.backend.common.FileSplitFormat import FileSplitFormat, FileSplitEntry

from py_mips_disasm.backend.mips.MipsFileBase import FileBase
from py_mips_disasm.backend.mips.MipsRelocZ64 import RelocZ64
from py_mips_disasm.backend.mips.FilesHandlers import createSectionFromSplitEntry

from .MipsFileGeneric import FileGeneric

from .ZeldaTables import OverlayTableEntry


class FileOverlay(FileGeneric):
    def __init__(self, array_of_bytes: bytearray, filename: str, context: Context, relocSection: RelocZ64, tableEntry: OverlayTableEntry | None = None, splitsData: FileSplitFormat | None = None, vramStartParam: int = -1):
        super().__init__(array_of_bytes, filename, context)

        self.vRamStart = vramStartParam

        if tableEntry is not None:
            self.vRamStart = tableEntry.vramStart

        for subfileVram, subfileData in context.files.items():
            if filename == subfileData.name:
                self.vRamStart = subfileVram
                break


        self.reloc = relocSection
        self.reloc.parent = self
        if self.reloc.vRamStart <= 0:
            self.reloc.vRamStart = self.vRamStart
            if self.vRamStart > -1:
                relocStart = relocSection.textSize + relocSection.dataSize + relocSection.rodataSize
                if relocSection.differentSegment:
                    relocStart += relocSection.bssSize
                self.reloc.vRamStart = self.vRamStart + relocStart


        self.splitsDataList: List[FileSplitEntry] = []
        if splitsData is not None and len(splitsData) > 0:
            for splitEntry in splitsData:
                self.splitsDataList.append(splitEntry)
        else:
            vram = self.vRamStart

            start = 0
            end = 0
            for i in range(len(FileSections_ListBasic)):
                sectionType = FileSections_ListBasic[i]
                sectionSize = relocSection.sectionSizes[sectionType]

                if i != 0:
                    start += relocSection.sectionSizes[FileSections_ListBasic[i-1]]
                end += relocSection.sectionSizes[sectionType]

                if sectionSize == 0:
                    # There's no need to disassemble empty sections
                    continue

                if self.vRamStart > 0:
                    vram = self.vRamStart + start
                splitEntry = FileSplitEntry(start, vram, filename, sectionType, end, False, False)
                self.splitsDataList.append(splitEntry)


        for splitEntry in self.splitsDataList:
            if self.vRamStart < 0:
                self.vRamStart = splitEntry.vram

            f = createSectionFromSplitEntry(splitEntry, self.bytes, splitEntry.fileName, context)
            f.parent = self
            f.setCommentOffset(splitEntry.offset)

            self.sectionsDict[splitEntry.section][splitEntry.fileName] = f


    def setVRamStart(self, vRamStart: int):
        super().setVRamStart(vRamStart)
        if not self.reloc.differentSegment:
            self.reloc.vRamStart = vRamStart

    def getHash(self) -> str:
        bytes = bytearray(0)
        for sectDict in self.sectionsDict.values():
            for section in sectDict.values():
                bytes += section.bytes
        bytes += self.reloc.bytes
        return disasm_Utils.getStrHash(bytes)

    def analyze(self):
        for entry in self.reloc.entries:
            section = entry.getSectionName()
            # type_name = entry.getTypeName()
            offset = entry.offset
            if entry.reloc == 0:
                continue

            sectionType = FileSectionType.fromStr(section)
            for subFile in self.sectionsDict[sectionType].values():
                subFile.pointersOffsets.add(offset)

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
