#!/usr/bin/python3

from __future__ import annotations

import argparse

from py_mips_disasm.backend.common.Utils import *
from py_mips_disasm.backend.common.GlobalConfig import GlobalConfig
from py_mips_disasm.backend.common.Context import Context
from py_mips_disasm.backend.common.FileSectionType import FileSectionType
from py_mips_disasm.backend.common.FileSplitFormat import FileSplitFormat

from py_mips_disasm.backend.mips.MipsText import Text

from mips.MipsFileGeneric import FileGeneric
from mips.MipsFileOverlay import FileOverlay
from mips.MipsFileSplits import FileSplits
from mips.ZeldaTables import DmaEntry, contextReadVariablesCsv, contextReadFunctionsCsv, getDmaAddresses, OverlayTableEntry
from mips import ZeldaOffsets

def disassembleFile(version: str, filename: str, game: str, outputfolder: str, context: Context, dmaAddresses: Dict[str, DmaEntry], vram: int = -1, textend: int = -1):
    is_overlay = filename.startswith("ovl_")

    path = os.path.join(game, version, "baserom", filename)

    array_of_bytes = readFileAsBytearray(path)
    if len(array_of_bytes) == 0:
        eprint(f"File '{path}' not found!")
        exit(-1)

    splitsData = None
    tablePath = os.path.join(game, version, "tables", f"files_{filename}.csv")
    if os.path.exists(tablePath):
        # print(tablePath)
        splitsData = FileSplitFormat()
        splitsData.readCsvFile(tablePath)

    if is_overlay:
        print("Overlay detected. Parsing...")

        tableEntry = None
        # TODO
        if filename in dmaAddresses:
            dmaEntry = dmaAddresses[filename]

            codePath = os.path.join(game, version, "baserom", "code")

            if os.path.exists(codePath) and version in ZeldaOffsets.offset_ActorOverlayTable[game]:
                tableOffset = ZeldaOffsets.offset_ActorOverlayTable[game][version]
                if tableOffset != 0x0:
                    codeData = readFileAsBytearray(codePath)
                    i = 0
                    while i < ZeldaOffsets.ActorIDMax[game]:
                        entry = OverlayTableEntry(codeData[tableOffset + i*0x20 : tableOffset + (i+1)*0x20])
                        if entry.vromStart == dmaEntry.vromStart:
                            tableEntry = entry
                            break
                        i += 1

        f = FileOverlay(array_of_bytes, filename, context, tableEntry=tableEntry)
    elif filename in ("code", "boot", "n64dd"):
        print(f"{filename} detected. Parsing...")
        f = FileSplits(array_of_bytes, filename, context, splitsData)
    else:
        print("Unknown file type. Assuming .text. Parsing...")

        text_data = array_of_bytes
        if textend >= 0:
            print(f"Parsing until offset {toHex(textend, 2)}")
            text_data = array_of_bytes[:textend]

        f = Text(text_data, filename, context)

    if vram >= 0:
        print(f"Using VRAM {toHex(vram, 8)[2:]}")
        f.setVRamStart(vram)

    f.analyze()

    print()
    print(f"Found {f.nFuncs} functions.")

    new_file_folder = os.path.join(outputfolder, filename)
    os.makedirs(new_file_folder, exist_ok=True)
    new_file_path = os.path.join(new_file_folder, filename)

    nBoundaries: int = 0
    if isinstance(f, FileGeneric):
        for name, text in f.sectionsDict[FileSectionType.Text].items():
            assert(isinstance(text, Text))
            nBoundaries += len(text.fileBoundaries)
    else:
        nBoundaries += len(f.fileBoundaries)
    if nBoundaries > 0:
        print(f"Found {nBoundaries} file boundaries.")

    print(f"Writing files to {new_file_folder}")
    f.saveToFile(new_file_path)

    print()
    print("Disassembling complete!")
    print("Goodbye.")


def disassemblerMain():
    description = ""
    parser = argparse.ArgumentParser(description=description)
    choices = ["oot", "mm"]
    parser.add_argument("game", help="Game to disassemble.", choices=choices)
    parser.add_argument("version", help="Select which baserom folder will be used. Example: ique_cn would look up in folder baserom_ique_cn")
    parser.add_argument("file", help="File to be disassembled from the baserom folder.")
    parser.add_argument("outputfolder", help="Path to output folder.")
    parser.add_argument("--vram", help="Set the VRAM address for unknown files.", default="-1")
    parser.add_argument("--text-end-offset", help="Set the offset of the end of .text section for unknown files.", default="-1")
    parser.add_argument("--disable-asm-comments", help="Disables the comments in assembly code.", action="store_true")
    parser.add_argument("--save-context", help="Saves the context to a file. The provided filename will be suffixed with the corresponding version.", metavar="FILENAME")
    args = parser.parse_args()

    GlobalConfig.REMOVE_POINTERS = False
    GlobalConfig.IGNORE_BRANCHES = False
    GlobalConfig.WRITE_BINARY = False
    GlobalConfig.ASM_COMMENT = not args.disable_asm_comments
    GlobalConfig.PRODUCE_SYMBOLS_PLUS_OFFSET = True
    # GlobalConfig.TRUST_USER_FUNCTIONS = True
    # GlobalConfig.DISASSEMBLE_UNKNOWN_INSTRUCTIONS = args.disasm_unknown
    # GlobalConfig.VERBOSE = args.verbose
    # GlobalConfig.QUIET = args.quiet

    context = Context()
    context.fillDefaultBannedSymbols()
    context.fillLibultraSymbols()
    context.fillHardwareRegs()
    context.readFunctionMap(args.version)
    contextReadVariablesCsv(context, args.game, args.version)
    contextReadFunctionsCsv(context, args.game, args.version)
    dmaAddresses: Dict[str, DmaEntry] = getDmaAddresses(args.game, args.version)

    disassembleFile(args.version, args.file, args.game, args.outputfolder, context, dmaAddresses, int(args.vram, 16), int(args.text_end_offset, 16))

    if args.save_context is not None:
        head, tail = os.path.split(args.save_context)
        if head != "":
            os.makedirs(head, exist_ok=True)
        context.saveContextToFile(args.save_context)


if __name__ == "__main__":
    disassemblerMain()
