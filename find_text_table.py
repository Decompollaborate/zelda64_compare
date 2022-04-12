#!/usr/bin/env python3

import argparse
import mmap
import os
import struct
import sys

# ===================================================
#   Util
# ===================================================

def as_hword_list(b):
    if len(b) % 2 != 0:
        return []
    return [h[0] for h in struct.iter_unpack(">H", b)]

def as_word_list(b):
    if len(b) % 4 != 0:
        return []
    return [i[0] for i in struct.iter_unpack(">I", b)]

def as_main_message_table(b):
    if len(b) % 8 != 0:
        return []
    return [(e[0], (e[1] >> 4) & 0xF, e[1] & 0xF, e[2]) for e in [i for i in struct.iter_unpack(">HBxI", b)]]

def segmented_to_offset(address):
    return address & 0x00FFFFFF


# ===================================================
#   message entry tables
# ===================================================

textbox_type = {
    0: "TEXTBOX_TYPE_BLACK",
    1: "TEXTBOX_TYPE_WOODEN",
    2: "TEXTBOX_TYPE_BLUE",
    3: "TEXTBOX_TYPE_OCARINA",
    4: "TEXTBOX_TYPE_NONE_BOTTOM",
    5: "TEXTBOX_TYPE_NONE_NO_SHADOW",
    0xB: "TEXTBOX_TYPE_CREDITS",
}

textbox_ypos = {
    0: "TEXTBOX_POS_VARIABLE",
    1: "TEXTBOX_POS_TOP",
    2: "TEXTBOX_POS_BOTTOM",
    3: "TEXTBOX_POS_MIDDLE",
}

# First message entry in JPN text table
JPN_FIRST_MESSAGE = bytes.fromhex("0001230008000000")
# First message entry in NES text table
NES_FIRST_MESSAGE = bytes.fromhex("0001230007000000")
# First message entry in Staff text table
STAFF_FIRST_MESSAGE = bytes.fromhex("0500B00007000000")
# Terminator for main text tables (JPN/NES/Staff)
MAIN_LAST_MESSAGE = bytes.fromhex("FFFF000000000000")
# # Terminator for sub text tables (FRA/GER on PAL)
# SUB_LAST_MESSAGE  = bytes.fromhex("00000000")

regionIsPAL = True

jpn_message_entry_table_offset   = 0
nes_message_entry_table_offset   = 0
nes_message_entry_table_end      = 0
ger_message_entry_table_offset   = 0
fra_message_entry_table_offset   = 0
staff_message_entry_table_offset = 0
staff_message_entry_table_end    = 0

jpn_message_entry_table   = []
nes_message_entry_table   = []
ger_message_entry_table   = []
fra_message_entry_table   = []
staff_message_entry_table = []

pal_combined_message_entry_table = []

def findTextTablesMMap(file):
    global jpn_message_entry_table_offset
    global nes_message_entry_table_offset
    global nes_message_entry_table_end
    global ger_message_entry_table_offset
    global fra_message_entry_table_offset
    global staff_message_entry_table_offset
    global staff_message_entry_table_end
    global regionIsPAL

    with open(file, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0)

        jpn_message_entry_table_offset = ger_message_entry_table_offset = fra_message_entry_table_offset = 0

        # Look backwards for nes_message_entry_table
        nes_message_entry_table_offset = mm.rfind(NES_FIRST_MESSAGE)
        if nes_message_entry_table_offset == -1:
            return -1

        # Look forwards for end of nes_message_entry_table
        nes_message_entry_table_end = mm.find(MAIN_LAST_MESSAGE, nes_message_entry_table_offset)
        nes_message_entry_table_end += 8

        # Look forwards for staff
        staff_message_entry_table_offset = mm.find(STAFF_FIRST_MESSAGE, nes_message_entry_table_end)
        # Look forwards for staff end
        staff_message_entry_table_end = mm.find(MAIN_LAST_MESSAGE, staff_message_entry_table_offset)
        staff_message_entry_table_end += 8

        if nes_message_entry_table_end == staff_message_entry_table_offset:
            regionIsPAL = False
            # NTSC, look backwards for jpn_message_entry_table
            jpn_message_entry_table_offset = mm.rfind(JPN_FIRST_MESSAGE, 0, nes_message_entry_table_offset)
        else:
            regionIsPAL = True
            # PAL, determine remaining offsets using arithmetic
            ger_message_entry_table_offset = nes_message_entry_table_end
            fra_message_entry_table_offset = (nes_message_entry_table_end + staff_message_entry_table_offset) // 2

        if not regionIsPAL:
            print(f"jpn_message_entry_table_offset: {jpn_message_entry_table_offset:X}")
            print(f"nes_message_entry_table_offset: {nes_message_entry_table_offset:X}")
        else:
            print(f"nes_message_entry_table_offset: {nes_message_entry_table_offset:X}")
            print(f"ger_message_entry_table_offset: {ger_message_entry_table_offset:X}")
            print(f"fra_message_entry_table_offset: {fra_message_entry_table_offset:X}")

        print(f"staff_message_entry_table_offset: {staff_message_entry_table_offset:X}")
        print(f"staff_message_entry_table_end: {staff_message_entry_table_end:X}")
    
    return 0

def read_tables(file):
    global jpn_message_entry_table
    global nes_message_entry_table
    global ger_message_entry_table
    global fra_message_entry_table

    global pal_combined_message_entry_table
    global staff_message_entry_table

    with open(file, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0)

        nes_message_entry_table = as_main_message_table(mm[nes_message_entry_table_offset:nes_message_entry_table_end])
        if len(nes_message_entry_table) == 0:
            print("nes_message_entry_table not found", file=sys.stderr)
            exit(1)

        if regionIsPAL:
            # For PAL, the same textIds are used for every table
            ger_message_entry_table = as_word_list(mm[ger_message_entry_table_offset:  fra_message_entry_table_offset])
            if len(ger_message_entry_table) == 0:
                print("ger_message_entry_table not found", file=sys.stderr)
                exit(1)

            fra_message_entry_table = as_word_list(mm[fra_message_entry_table_offset:staff_message_entry_table_offset])
            if len(fra_message_entry_table) == 0:
                print("fra_message_entry_table not found", file=sys.stderr)
                exit(1)

            subIndex = 0
            for mainIndex in range(len(nes_message_entry_table)):
                entry = nes_message_entry_table[mainIndex]
                if entry[0] != 0xFFFC:
                    pal_combined_message_entry_table.append((*entry, ger_message_entry_table[subIndex], fra_message_entry_table[subIndex]))
                    subIndex += 1
                else:
                    pal_combined_message_entry_table.append((*entry, None, None))

        else:
            # For non-PAL, the textIds are distinct for jpn and nes
            jpn_message_entry_table = as_main_message_table(mm[jpn_message_entry_table_offset:nes_message_entry_table_offset])
            if len(jpn_message_entry_table) == 0:
                print("jpn_message_entry_table not found", file=sys.stderr)
                exit(1)

            # for i in range(max(len(nes_message_entry_table),len(nes_message_entry_table))):
            #     if i < len(jpn_message_entry_table):
            #         msg = jpn_message_entry_table[i]
            #         print(f"0x{msg[0]:X}, {msg[1]}, {msg[2]}, 0x{msg[3]:X}, ", end="")
            #     else:
            #         print(",,,,", end="")
            #     if i < len(nes_message_entry_table):
            #         msg = nes_message_entry_table[i]
            #         print(f"0x{msg[0]:X}, {msg[1]}, {msg[2]}, 0x{msg[3]:X}")

        staff_message_entry_table = as_main_message_table(mm[staff_message_entry_table_offset:staff_message_entry_table_end])









def findAndExtractTextTables(file):
    global regionIsPAL

    with open(file, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0)

        jpn_message_entry_table_offset = ger_message_entry_table_offset = fra_message_entry_table_offset = 0

        # Look backwards for nes_message_entry_table
        nes_message_entry_table_offset = mm.rfind(NES_FIRST_MESSAGE)
        if nes_message_entry_table_offset == -1:
            return -1

        # Look forwards for end of nes_message_entry_table
        nes_message_entry_table_end = mm.find(MAIN_LAST_MESSAGE, nes_message_entry_table_offset)
        nes_message_entry_table_end += 8

        # Look forwards for staff
        staff_message_entry_table_offset = mm.find(STAFF_FIRST_MESSAGE, nes_message_entry_table_end)
        # Look forwards for staff end
        staff_message_entry_table_end = mm.find(MAIN_LAST_MESSAGE, staff_message_entry_table_offset)
        staff_message_entry_table_end += 8

        if nes_message_entry_table_end == staff_message_entry_table_offset:
            regionIsPAL = False
            # NTSC, look backwards for jpn_message_entry_table
            jpn_message_entry_table_offset = mm.rfind(JPN_FIRST_MESSAGE, 0, nes_message_entry_table_offset)
        else:
            regionIsPAL = True
            # PAL, determine remaining offsets using arithmetic
            ger_message_entry_table_offset = nes_message_entry_table_end
            fra_message_entry_table_offset = (nes_message_entry_table_end + staff_message_entry_table_offset) // 2

        if not regionIsPAL:
            print(f"jpn_message_entry_table_offset: {jpn_message_entry_table_offset:X}")
            print(f"nes_message_entry_table_offset: {nes_message_entry_table_offset:X}")
            # print(f"{nes_message_entry_table_offset:X},{jpn_message_entry_table_offset:X},", end="")
        else:
            print(f"nes_message_entry_table_offset: {nes_message_entry_table_offset:X}")
            print(f"ger_message_entry_table_offset: {ger_message_entry_table_offset:X}")
            print(f"fra_message_entry_table_offset: {fra_message_entry_table_offset:X}")
            # print(f"{nes_message_entry_table_offset:X},{ger_message_entry_table_offset:X},{fra_message_entry_table_offset:X},", end="")

        print(f"staff_message_entry_table_offset: {staff_message_entry_table_offset:X}")
        print(f"staff_message_entry_table_end: {staff_message_entry_table_end:X}")
        # print(f"{staff_message_entry_table_offset:X},{staff_message_entry_table_end:X}")














def main():
    description = "Find the text tables from a provided `code` file"
    epilog = ""

    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("code", help="`code` file to search.")
    # parser.add_argument("-j", help="jpn_message_static")
    args = parser.parse_args()

    # findTextTables(args.code)
    # findTextTablesManual(args.code)

    findTextTablesMMap(args.code)
    read_tables(args.code)

    # if args.j:
    #     read_jpn()

    # findAndExtractTextTables(args.code)

if __name__ == "__main__":
    main()
