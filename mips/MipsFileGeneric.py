#!/usr/bin/env python3

from __future__ import annotations

import py_mips_disasm.backend.common.Utils as disasm_Utils
from py_mips_disasm.backend.common.GlobalConfig import GlobalConfig
from py_mips_disasm.backend.common.Context import Context
from py_mips_disasm.backend.common.FileSectionType import FileSectionType

from py_mips_disasm.backend.mips.MipsFileBase import FileBase, createEmptyFile
from py_mips_disasm.backend.mips.MipsSection import Section
from py_mips_disasm.backend.mips.MipsText import Text
from py_mips_disasm.backend.mips.MipsData import Data
from py_mips_disasm.backend.mips.MipsRodata import Rodata
from py_mips_disasm.backend.mips.MipsBss import Bss

# Not intended to be instanced
class FileGeneric(FileBase):
    def __init__(self, array_of_bytes: bytearray, filename: str, context: Context):
        super().__init__(array_of_bytes, filename, context)

        self.sectionsDict: dict[FileSectionType, dict[str, Section]] = {
            FileSectionType.Text: dict(),
            FileSectionType.Data: dict(),
            FileSectionType.Rodata: dict(),
            FileSectionType.Bss: dict(),
        }

        self.initVarsAddress = -1

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
        for sectDict in self.sectionsDict.values():
            for section in sectDict.values():
                section.analyze()

    def compareToFile(self, other_file: FileBase):
        if isinstance(other_file, FileGeneric):
            filesections = {
                "text": dict(),
                "data": dict(),
                "rodata": dict(),
                # "bss": dict(),
            }

            # TODO: avoid code duplication here

            for section_name, section in self.sectionsDict[FileSectionType.Text].items():
                if section_name in other_file.sectionsDict[FileSectionType.Text]:
                    other_section = other_file.sectionsDict[FileSectionType.Text][section_name]
                    filesections["text"][section_name] = section.compareToFile(other_section)
                else:
                    filesections["text"][section_name] = section.compareToFile(createEmptyFile())
            for section_name, other_section in other_file.sectionsDict[FileSectionType.Text].items():
                if section_name in self.sectionsDict[FileSectionType.Text]:
                    section = self.sectionsDict[FileSectionType.Text][section_name]
                    if section_name not in filesections["text"]:
                        filesections["text"][section_name] = section.compareToFile(other_section)
                else:
                    filesections["text"][section_name] = createEmptyFile().compareToFile(other_section)

            for section_name, section in self.sectionsDict[FileSectionType.Data].items():
                if section_name in other_file.sectionsDict[FileSectionType.Data]:
                    other_section = other_file.sectionsDict[FileSectionType.Data][section_name]
                    filesections["data"][section_name] = section.compareToFile(other_section)
                else:
                    filesections["data"][section_name] = section.compareToFile(createEmptyFile())
            for section_name, other_section in other_file.sectionsDict[FileSectionType.Data].items():
                if section_name in self.sectionsDict[FileSectionType.Data]:
                    section = self.sectionsDict[FileSectionType.Data][section_name]
                    if section_name not in filesections["data"]:
                        filesections["data"][section_name] = section.compareToFile(other_section)
                else:
                    filesections["data"][section_name] = createEmptyFile().compareToFile(other_section)

            for section_name, section in self.sectionsDict[FileSectionType.Rodata].items():
                if section_name in other_file.sectionsDict[FileSectionType.Rodata]:
                    other_section = other_file.sectionsDict[FileSectionType.Rodata][section_name]
                    filesections["rodata"][section_name] = section.compareToFile(other_section)
                else:
                    filesections["rodata"][section_name] = section.compareToFile(createEmptyFile())
            for section_name, other_section in other_file.sectionsDict[FileSectionType.Rodata].items():
                if section_name in self.sectionsDict[FileSectionType.Rodata]:
                    section = self.sectionsDict[FileSectionType.Rodata][section_name]
                    if section_name not in filesections["rodata"]:
                        filesections["rodata"][section_name] = section.compareToFile(other_section)
                else:
                    filesections["rodata"][section_name] = createEmptyFile().compareToFile(other_section)

            return {"filesections": filesections}

        return super().compareToFile(other_file)

    def blankOutDifferences(self, other_file: FileBase) -> bool:
        if not GlobalConfig.REMOVE_POINTERS:
            return False

        if not isinstance(other_file, FileGeneric):
            return False

        was_updated = False
        for section_name, section in self.sectionsDict[FileSectionType.Text].items():
            if section_name in other_file.sectionsDict[FileSectionType.Text]:
                other_section = other_file.sectionsDict[FileSectionType.Text][section_name]
                was_updated = section.blankOutDifferences(other_section) or was_updated
        for section_name, other_section in other_file.sectionsDict[FileSectionType.Text].items():
            if section_name in self.sectionsDict[FileSectionType.Text]:
                section = self.sectionsDict[FileSectionType.Text][section_name]
                was_updated = section.blankOutDifferences(other_section) or was_updated

        for section_name, section in self.sectionsDict[FileSectionType.Data].items():
            if section_name in other_file.sectionsDict[FileSectionType.Data]:
                other_section = other_file.sectionsDict[FileSectionType.Data][section_name]
                was_updated = section.blankOutDifferences(other_section) or was_updated
        for section_name, other_section in other_file.sectionsDict[FileSectionType.Data].items():
            if section_name in self.sectionsDict[FileSectionType.Data]:
                section = self.sectionsDict[FileSectionType.Data][section_name]
                was_updated = section.blankOutDifferences(other_section) or was_updated

        for section_name, section in self.sectionsDict[FileSectionType.Rodata].items():
            if section_name in other_file.sectionsDict[FileSectionType.Rodata]:
                other_section = other_file.sectionsDict[FileSectionType.Rodata][section_name]
                was_updated = section.blankOutDifferences(other_section) or was_updated
        for section_name, other_section in other_file.sectionsDict[FileSectionType.Rodata].items():
            if section_name in self.sectionsDict[FileSectionType.Rodata]:
                section = self.sectionsDict[FileSectionType.Rodata][section_name]
                was_updated = section.blankOutDifferences(other_section) or was_updated

        for section_name, section in self.sectionsDict[FileSectionType.Bss].items():
            if section_name in other_file.sectionsDict[FileSectionType.Bss]:
                other_section = other_file.sectionsDict[FileSectionType.Bss][section_name]
                was_updated = section.blankOutDifferences(other_section) or was_updated
        for section_name, other_section in other_file.sectionsDict[FileSectionType.Bss].items():
            if section_name in self.sectionsDict[FileSectionType.Bss]:
                section = self.sectionsDict[FileSectionType.Bss][section_name]
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
