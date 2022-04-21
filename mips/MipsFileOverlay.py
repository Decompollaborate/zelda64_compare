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


        relocSection.parent = self
        if relocSection.vRamStart <= 0:
            relocSection.vRamStart = self.vRamStart
            if self.vRamStart > -1:
                relocStart = relocSection.textSize + relocSection.dataSize + relocSection.rodataSize
                if relocSection.differentSegment:
                    relocStart += relocSection.bssSize
                relocSection.vRamStart = self.vRamStart + relocStart


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

                if sectionType == FileSectionType.Bss:
                    # bss is after reloc when the relocation is on the same segment
                    if not relocSection.differentSegment:
                        start += relocSection.size
                        end += relocSection.size

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

        self.sectionsDict[FileSectionType.Reloc][filename] = relocSection


    def analyze(self):
        for filename, relocSection in self.sectionsDict[FileSectionType.Reloc].items():
            assert isinstance(relocSection, RelocZ64)
            for entry in relocSection.entries:
                sectionType = entry.getSectionType()
                if entry.reloc == 0:
                    continue

                for subFile in self.sectionsDict[sectionType].values():
                    subFile.pointersOffsets.add(entry.offset)

        super().analyze()
