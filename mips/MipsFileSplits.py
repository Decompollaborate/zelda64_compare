#!/usr/bin/env python3

from __future__ import annotations

from typing import List
import py_mips_disasm.backend.common.Utils as disasm_Utils
from py_mips_disasm.backend.common.GlobalConfig import GlobalConfig
from py_mips_disasm.backend.common.Context import Context
from py_mips_disasm.backend.common.FileSectionType import FileSectionType, FileSections_ListBasic, FileSections_ListAll
from py_mips_disasm.backend.common.FileSplitFormat import FileSplitFormat, FileSplitEntry

from py_mips_disasm.backend.mips.MipsFileBase import FileBase, createEmptyFile
from py_mips_disasm.backend.mips.MipsSection import Section
from py_mips_disasm.backend.mips.MipsText import Text
from py_mips_disasm.backend.mips.MipsRelocZ64 import RelocZ64
from py_mips_disasm.backend.mips.FilesHandlers import createSectionFromSplitEntry


class FileSplits(FileBase):
    def __init__(self, array_of_bytes: bytearray, filename: str, context: Context, splitsData: FileSplitFormat | None = None, relocSection: RelocZ64|None = None, vramStartParam: int = -1):
        super().__init__(array_of_bytes, filename, context)

        self.sectionsDict: dict[FileSectionType, dict[str, Section]] = {
            FileSectionType.Text: dict(),
            FileSectionType.Data: dict(),
            FileSectionType.Rodata: dict(),
            FileSectionType.Bss: dict(),
            FileSectionType.Reloc: dict(),
        }

        self.vRamStart = vramStartParam

        for subfileVram, subfileData in context.files.items():
            if filename == subfileData.name:
                self.vRamStart = subfileVram
                break

        self.splitsDataList: List[FileSplitEntry] = []

        if relocSection is not None:
            relocSection.parent = self
            if relocSection.vRamStart <= 0:
                relocSection.vRamStart = self.vRamStart
                if self.vRamStart > -1:
                    relocStart = relocSection.textSize + relocSection.dataSize + relocSection.rodataSize
                    if relocSection.differentSegment:
                        relocStart += relocSection.bssSize
                    relocSection.vRamStart = self.vRamStart + relocStart
            self.sectionsDict[FileSectionType.Reloc][filename] = relocSection

        if splitsData is None and relocSection is None:
            self.sectionsDict[FileSectionType.Text][filename] = Text(self.bytes, filename, context)
        elif splitsData is not None and len(splitsData) > 0:
            for splitEntry in splitsData:
                self.splitsDataList.append(splitEntry)
        elif relocSection is not None:
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

    @property
    def nFuncs(self) -> int:
        nFuncs = 0
        for f in self.sectionsDict[FileSectionType.Text].values():
            assert(isinstance(f, Text))
            text: Text = f
            nFuncs += text.nFuncs
        return nFuncs

    def setVRamStart(self, vRamStart: int):
        super().setVRamStart(vRamStart)
        for sectDict in self.sectionsDict.values():
            for section in sectDict.values():
                section.setVRamStart(vRamStart)

    def getHash(self) -> str:
        bytes = bytearray(0)
        for sectDict in self.sectionsDict.values():
            for section in sectDict.values():
                bytes += section.bytes
        return disasm_Utils.getStrHash(bytes)

    def analyze(self):
        for filename, relocSection in self.sectionsDict[FileSectionType.Reloc].items():
            assert isinstance(relocSection, RelocZ64)
            for entry in relocSection.entries:
                sectionType = entry.getSectionType()
                if entry.reloc == 0:
                    continue

                for subFile in self.sectionsDict[sectionType].values():
                    subFile.pointersOffsets.add(entry.offset)

        for sectDict in self.sectionsDict.values():
            for section in sectDict.values():
                section.analyze()

    def compareToFile(self, other_file: FileBase):
        if isinstance(other_file, FileSplits):
            filesections = {
                FileSectionType.Text: dict(),
                FileSectionType.Data: dict(),
                FileSectionType.Rodata: dict(),
                FileSectionType.Bss: dict(),
                FileSectionType.Reloc: dict(),
            }

            for sectionType in FileSections_ListAll:
                for section_name, section in self.sectionsDict[sectionType].items():
                    if section_name in other_file.sectionsDict[sectionType]:
                        other_section = other_file.sectionsDict[sectionType][section_name]
                        filesections[sectionType][section_name] = section.compareToFile(other_section)
                    else:
                        filesections[sectionType][section_name] = section.compareToFile(createEmptyFile())
                for section_name, other_section in other_file.sectionsDict[sectionType].items():
                    if section_name in self.sectionsDict[sectionType]:
                        section = self.sectionsDict[sectionType][section_name]
                        if section_name not in filesections[sectionType]:
                            filesections[sectionType][section_name] = section.compareToFile(other_section)
                    else:
                        filesections[sectionType][section_name] = createEmptyFile().compareToFile(other_section)

            return {"filesections": filesections}

        return super().compareToFile(other_file)

    def blankOutDifferences(self, other_file: FileBase) -> bool:
        if not GlobalConfig.REMOVE_POINTERS:
            return False

        if not isinstance(other_file, FileSplits):
            return False

        was_updated = False
        for sectionType in FileSections_ListAll:
            for section_name, section in self.sectionsDict[sectionType].items():
                if section_name in other_file.sectionsDict[sectionType]:
                    other_section = other_file.sectionsDict[sectionType][section_name]
                    was_updated = section.blankOutDifferences(other_section) or was_updated
            for section_name, other_section in other_file.sectionsDict[sectionType].items():
                if section_name in self.sectionsDict[sectionType]:
                    section = self.sectionsDict[sectionType][section_name]
                    was_updated = section.blankOutDifferences(other_section) or was_updated

        return was_updated

    def removePointers(self) -> bool:
        if not GlobalConfig.REMOVE_POINTERS:
            return False

        was_updated = False
        for sectDict in self.sectionsDict.values():
            for section in sectDict.values():
                was_updated = section.removePointers() or was_updated

        return was_updated

    def updateBytes(self):
        for sectDict in self.sectionsDict.values():
            for section in sectDict.values():
                section.updateBytes()

    def saveToFile(self, filepath: str):
        for sectDict in self.sectionsDict.values():
            for name, section in sectDict.items():
                if name != "" and not filepath.endswith("/"):
                    name = " " + name
                section.saveToFile(filepath + name)
