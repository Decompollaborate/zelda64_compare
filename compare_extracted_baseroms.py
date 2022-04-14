#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os

import py_mips_disasm.backend.common.Utils as disasm_Utils
from py_mips_disasm.backend.common.GlobalConfig import GlobalConfig
from py_mips_disasm.backend.common.Context import Context
from py_mips_disasm.backend.common.FileSplitFormat import FileSplitFormat

from py_mips_disasm.backend.mips.MipsSection import Section

from mips.MipsFileOverlay import FileOverlay
from mips.MipsFileSplits import FileSplits
from mips.ZeldaTables import contextReadVariablesCsv, contextReadFunctionsCsv


def print_result_different(comparison, indentation=0):
    if comparison['size_one'] != comparison['size_two']:
        div = round(comparison['size_two']/comparison['size_one'], 3)
        print((indentation * "\t") + f"Size doesn't match: {comparison['size_one']} vs {comparison['size_two']} (x{div}) ({comparison['size_two'] - comparison['size_one']})")
    else:
        print((indentation * "\t") + "Size matches.")
    print((indentation * "\t") + f"There are at least {comparison['diff_bytes']} bytes different, and {comparison['diff_words']} words different.")

def compare_baseroms(args, filelist):
    missing_in_one = set()
    missing_in_two = set()

    equals = 0
    different = 0

    context_one = Context()
    context_two = Context()
    context_one.fillDefaultBannedSymbols()
    context_one.fillLibultraSymbols()
    context_one.fillHardwareRegs()
    context_one.readFunctionMap(args.version1)
    context_two.fillDefaultBannedSymbols()
    context_two.fillLibultraSymbols()
    context_two.fillHardwareRegs()
    context_two.readFunctionMap(args.version2)
    contextReadVariablesCsv(context_one, args.game, args.version1)
    contextReadVariablesCsv(context_two, args.game, args.version2)
    contextReadFunctionsCsv(context_one, args.game, args.version1)
    contextReadFunctionsCsv(context_two, args.game, args.version2)

    for filename in filelist:
        filepath_one = os.path.join(args.game, args.version1, "baserom", filename)
        filepath_two = os.path.join(args.game, args.version2, "baserom", filename)

        if not os.path.exists(filepath_one):
            missing_in_one.add(filename)
            if args.print in ("all", "missing"):
                print(f"File {filename} does not exists in baserom.")
            continue

        if not os.path.exists(filepath_two):
            missing_in_two.add(filename)
            if args.print in ("all", "missing"):
                print(f"File {filename} does not exists in other_baserom.")
            continue

        file_one_data = disasm_Utils.readFileAsBytearray(filepath_one)
        file_two_data = disasm_Utils.readFileAsBytearray(filepath_two)

        splitsDataOne = None
        splitsDataTwo = None
        tablePath = os.path.join(args.game, args.version1, "tables", f"files_{filename}.csv")
        if os.path.exists(tablePath):
            splitsDataOne = FileSplitFormat()
            splitsDataOne.readCsvFile(tablePath)
        tablePath = os.path.join(args.game, args.version2, "tables", f"files_{filename}.csv")
        if os.path.exists(tablePath):
            splitsDataTwo = FileSplitFormat()
            splitsDataTwo.readCsvFile(tablePath)

        if filename.startswith("ovl_"):
            file_one = FileOverlay(file_one_data, filename, context_one)
            file_two = FileOverlay(file_two_data, filename, context_two)
        elif filename in ("code", "boot", "n64dd"):
            file_one = FileSplits(file_one_data, filename, context_one, splitsDataOne)
            file_two = FileSplits(file_two_data, filename, context_two, splitsDataTwo)
        else:
            file_one = Section(file_one_data, filename, context_one)
            file_two = Section(file_two_data, filename, context_two)

        file_one.analyze()
        file_two.analyze()

        if GlobalConfig.REMOVE_POINTERS:
            both_updated = file_one.blankOutDifferences(file_two)
            one_updated = file_one.removePointers()
            two_updated = file_two.removePointers()
            if both_updated or one_updated:
                file_one.updateBytes()
            if both_updated or two_updated:
                file_two.updateBytes()

        comparison = file_one.compareToFile(file_two)

        if comparison["equal"]:
            equals += 1
            if args.print in ("all", "equals"):
                print(f"{filename} OK")
        else:
            different += 1
            if args.print in ("all", "diffs"):
                print(f"{filename} not OK")
                print_result_different(comparison, 1)

                if "filesections" in comparison:
                    for section_name in comparison["filesections"]:
                        section = comparison["filesections"][section_name]

                        if section["size_one"] == 0:
                            continue

                        if section["equal"] and args.print in ("all", "equals"):
                            print(f"\t\t{section_name} OK")
                        else:
                            print(f"\t\t{section_name} not OK")
                            print_result_different(section, 3)

    total = len(filelist)
    if total > 0:
        print()
        if args.print in ("all", "equals"):
            print(f"Equals:     {equals}/{total} ({round(100*equals/total, 2)}%)")
        if args.print in ("all", "diffs"):
            print(f"Differents: {different}/{total} ({round(100*different/total, 2)}%)")
        if args.print in ("all", "missing"):
            missing = len(missing_in_one)
            print(f"Missing:    {missing}/{total} ({round(100*missing/total, 2)}%)")
            print(f"Missing 2:  {len(missing_in_two)}")

def print_section_as_csv(args, index: int, filename: str, section_name: str, section: dict):
    equal = section["equal"]

    if equal and args.print not in ("all", "equals"):
        return
    if not equal and args.print not in ("all", "diffs"):
        return

    len_one = section["size_one"]
    len_two = section["size_two"]
    if len_one > 0 or len_two > 0:
        if len_one > 0:
            div = round(len_two/len_one, 3)
        else:
            div = "Inf"
        size_difference = len_two - len_one
        diff_bytes = section["diff_bytes"]
        diff_words = section["diff_words"]
        print(f'{index},{filename} {section_name},{equal},{len_one},{len_two},{div},{size_difference},{diff_bytes},{diff_words}', end="")
        if not args.dont_split_files:
            if "text" in section:
                print(f',{section["text"]["diff_opcode"]},{section["text"]["same_opcode_same_args"]}', end="")
            else:
                print(",,", end="")
        print()

def compare_to_csv(args, filelist):
    index = -1

    column1 = args.version1 if args.column1 is None else args.column1
    column2 = args.version2 if args.column2 is None else args.column2

    context_one = Context()
    context_two = Context()
    context_one.readFunctionMap(args.version1)
    context_two.readFunctionMap(args.version2)

    print(f"Index,File,Are equals,Size in {column1},Size in {column2},Size proportion,Size difference,Bytes different,Words different", end="")
    if not args.dont_split_files:
        print(",Opcodes difference,Same opcode but different arguments", end="")
    print(flush=True)

    for filename in filelist:
        filepath_one = os.path.join(args.game, args.version1, "baserom", filename)
        filepath_two = os.path.join(args.game, args.version2, "baserom", filename)

        index += 1

        #if args.filetype != "all" and args.filetype != filedata["type"]:
        #    continue

        file_one_data = disasm_Utils.readFileAsBytearray(filepath_one)
        file_two_data = disasm_Utils.readFileAsBytearray(filepath_two)

        equal = ""
        len_one = ""
        len_two = ""
        div = ""
        size_difference = ""
        diff_bytes = ""
        diff_words = ""
        comparison = dict()

        is_missing_in_one = len(file_one_data) == 0
        is_missing_in_two = len(file_two_data) == 0

        if is_missing_in_one or is_missing_in_two:
            if args.print not in ("all", "missing"):
                continue
            len_one = "" if is_missing_in_one else len(file_one_data)
            len_two = "" if is_missing_in_two else len(file_two_data)

            print(f'{index},{filename},{equal},{len_one},{len_two},{div},{size_difference},{diff_bytes},{diff_words}', end="")
            if not args.dont_split_files:
                print(",,", end="")
            print()

        else:
            splitsDataOne = None
            splitsDataTwo = None
            tablePath = os.path.join(args.game, args.version1, "tables", f"files_{filename}.csv")
            if os.path.exists(tablePath):
                splitsDataOne = FileSplitFormat()
                splitsDataOne.readCsvFile(tablePath)
            tablePath = os.path.join(args.game, args.version2, "tables", f"files_{filename}.csv")
            if os.path.exists(tablePath):
                splitsDataTwo = FileSplitFormat()
                splitsDataTwo.readCsvFile(tablePath)

            if not args.dont_split_files and filename.startswith("ovl_"):
                file_one = FileOverlay(file_one_data, filename, context_one)
                file_two = FileOverlay(file_two_data, filename, context_two)
            elif filename in ("code", "boot", "n64dd"):
                file_one = FileSplits(file_one_data, filename, context_one, splitsDataOne)
                file_two = FileSplits(file_two_data, filename, context_two, splitsDataTwo)
            else:
                file_one = Section(file_one_data, filename, context_one)
                file_two = Section(file_two_data, filename, context_two)

            file_one.analyze()
            file_two.analyze()

            if GlobalConfig.REMOVE_POINTERS:
                both_updated = file_one.blankOutDifferences(file_two)
                one_updated = file_one.removePointers()
                two_updated = file_two.removePointers()
                if both_updated or one_updated:
                    file_one.updateBytes()
                if both_updated or two_updated:
                    file_two.updateBytes()

            comparison = file_one.compareToFile(file_two)
            if "filesections" in comparison:
                for section_name in comparison["filesections"]:
                    section = comparison["filesections"][section_name]
                    for n, sub in section.items():
                        aux_section_name = section_name
                        if n != filename:
                            aux_section_name = f"{n} {section_name}"
                        print_section_as_csv(args, index, filename, aux_section_name, sub)
            else:
                print_section_as_csv(args, index, filename, "", comparison)


def main():
    description = ""

    epilog = """\
    """
    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    choices = ["oot", "mm"]
    parser.add_argument("game", help="Game to comapre.", choices=choices)
    parser.add_argument("version1", help="A version of the game to compare.")
    parser.add_argument("version2", help="A version of the game to compare.")
    parser.add_argument("filelist", help="Path to the filelist that will be used.")
    parser.add_argument("--print", help="Select what will be printed for a cleaner output. Default is 'all'.", choices=["all", "equals", "diffs", "missing"], default="all")
    parser.add_argument("--dont-split-files", help="Disables treating each section of a a file as separate files.", action="store_true")
    parser.add_argument("--no-csv", help="Don't print the output in csv format.", action="store_true")
    parser.add_argument("--ignore-words", help="A space separated list of hex numbers. Word differences will be ignored that starts in any of the provided arguments. Max value: FF", action="extend", nargs="+")
    parser.add_argument("--ignore-branches", help="Ignores the address of every branch, jump and jal.", action="store_true")
    parser.add_argument("--dont-remove-ptrs", help="Disable the pointer removal feature.", action="store_true")
    parser.add_argument("--column1", help="Name for column one (baserom) in the csv.", default=None)
    parser.add_argument("--column2", help="Name for column two (other_baserom) in the csv.", default=None)
    args = parser.parse_args()

    GlobalConfig.REMOVE_POINTERS = not args.dont_remove_ptrs
    GlobalConfig.IGNORE_BRANCHES = args.ignore_branches
    if args.ignore_words:
        for upperByte in args.ignore_words:
            GlobalConfig.IGNORE_WORD_LIST.add(int(upperByte, 16))
    # GlobalConfig.WRITE_BINARY = False
    # GlobalConfig.ASM_COMMENT = not args.disable_asm_comments
    GlobalConfig.PRODUCE_SYMBOLS_PLUS_OFFSET = True
    GlobalConfig.TRUST_USER_FUNCTIONS = True
    # GlobalConfig.DISASSEMBLE_UNKNOWN_INSTRUCTIONS = args.disasm_unknown
    # GlobalConfig.VERBOSE = args.verbose
    # GlobalConfig.QUIET = args.quiet

    filelist = disasm_Utils.readFile(args.filelist)

    if not args.no_csv:
        compare_to_csv(args, filelist)
    else:
        compare_baseroms(args, filelist)


if __name__ == "__main__":
    main()
