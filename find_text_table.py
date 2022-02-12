#!/usr/bin/python3

import argparse
import mmap
import os
from re import search
import struct

# First message entry in JPN text table
JPN_FIRST_MESSAGE = bytes.fromhex("0001230008000000")
# First message entry in NES text table
NES_FIRST_MESSAGE = bytes.fromhex("0001230007000000")
# First message entry in Staff text table
STAFF_FIRST_MESSAGE = bytes.fromhex("0500B00007000000")
# Terminator for main text tables (JPN/NES/Staff)
MAIN_LAST_MESSAGE = bytes.fromhex("FFFF000000000000")
# Terminator for sub text tables (FRA/GER on PAL)
SUB_LAST_MESSAGE  = bytes.fromhex("00000000")

def findTextTables(file):
    with open(file, "rb") as f:
        s = f.read()
        jpn_message_table_offset = s.find(JPN_FIRST_MESSAGE)
        if jpn_message_table_offset == -1:
            jpn_message_table_offset = 0
            print("jpn_message_table not found")
        else:
            print(f"jpn_message_table_offset: {jpn_message_table_offset:X}")

        f.seek(jpn_message_table_offset, os.SEEK_SET)
        cur_pos = f.tell()
        s = f.read()
        nes_message_table_offset = s.find(NES_FIRST_MESSAGE)
        if nes_message_table_offset == -1:
            nes_message_table_offset = 0
            print("nes_message_table not found")
        else:
            nes_message_table_offset += cur_pos
            print(f"nes_message_table_offset: {nes_message_table_offset:X}")
        
        f.seek(nes_message_table_offset, os.SEEK_SET)
        cur_pos = f.tell()
        s = f.read()

        if jpn_message_table_offset == 0:
            ger_message_table_offset = s.find(MAIN_LAST_MESSAGE)
            ger_message_table_offset += cur_pos + 8
            print(f"ger_message_table_offset: {ger_message_table_offset:X}")

            f.seek(ger_message_table_offset, os.SEEK_SET)
            cur_pos = f.tell()
            s = f.read()        

            fra_message_table_offset = s.find(SUB_LAST_MESSAGE)
            fra_message_table_offset += cur_pos + 4
            print(f"fra_message_table_offset: {fra_message_table_offset:X}")

            f.seek(fra_message_table_offset, os.SEEK_SET)
            cur_pos = f.tell()
            s = f.read()

            staff_message_table_offset = s.find(SUB_LAST_MESSAGE) 
            staff_message_table_offset += cur_pos + 4
        
        else:
            staff_message_table_offset = s.find(MAIN_LAST_MESSAGE)
            staff_message_table_offset += cur_pos + 8

        print(f"staff_message_table_offset: {staff_message_table_offset:X}")
        f.seek(staff_message_table_offset, os.SEEK_SET)
        cur_pos = f.tell()
        s = f.read()

        staff_message_table_end = s.find(MAIN_LAST_MESSAGE) 
        staff_message_table_end += cur_pos + 8
        print(f"staff_message_table_end: {staff_message_table_end:X}")

def findTextTablesReverse(file):
    # checks = 0

    with open(file, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0)

        # Look backwards for nes_message_table
        nes_message_table_offset = 0
        searchLength = len(NES_FIRST_MESSAGE)
        for i in range(len(mm) - searchLength, 0, -4):
            # checks += 1
            if bytes(mm[i:i+searchLength]) == NES_FIRST_MESSAGE:
                nes_message_table_offset = i
                break
        # print(f"nes_message_table_offset: {nes_message_table_offset:X}")
        
        if nes_message_table_offset == 0:
            return -1

        # Look forwards for end of nes_message_table
        nes_message_table_end = 0
        searchLength = len(MAIN_LAST_MESSAGE)
        for i in range(nes_message_table_offset, len(mm) - searchLength, 8):
            # checks += 1
            if bytes(mm[i:i+searchLength]) == MAIN_LAST_MESSAGE:
                nes_message_table_end = i + 8
                break
        # print(f"nes_message_end: {nes_message_table_end:X}")

        if nes_message_table_end == 0:
            return -1

        # Look forwards for staff
        staff_message_table_offset = 0
        searchLength = len(STAFF_FIRST_MESSAGE)
        for i in range(nes_message_table_end, len(mm) - searchLength, 4):
            # checks += 1
            if bytes(mm[i:i+searchLength]) == STAFF_FIRST_MESSAGE:
                staff_message_table_offset = i
                break
        # print(f"staff_message_table_offset: {staff_message_table_offset:X}")

        # Look forwards for staff end
        staff_message_table_end = 0
        searchLength = len(MAIN_LAST_MESSAGE)
        for i in range(staff_message_table_offset, len(mm) - searchLength, 8):
            # checks += 1
            if bytes(mm[i:i+searchLength]) == MAIN_LAST_MESSAGE:
                staff_message_table_end = i + 8
                break
        # print(f"staff_message_table_end: {staff_message_table_end:X}")

        if nes_message_table_end == staff_message_table_offset:
            # NTSC, look backwards for jpn_message_table
            jpn_message_table_offset = 0
            searchLength = len(JPN_FIRST_MESSAGE)
            for i in range(nes_message_table_offset - searchLength, 0, -8):
                # checks += 1
                if bytes(mm[i:i+searchLength]) == JPN_FIRST_MESSAGE:
                    jpn_message_table_offset = i
                    break
            # print(f"jpn_message_table_offset: {jpn_message_table_offset:X}")

            # print(f"nes_message_table_offset: {nes_message_table_offset:X}")
            # print(f"jpn_message_table_offset: {jpn_message_table_offset:X}")
            print(f"{nes_message_table_offset:X},{jpn_message_table_offset:X},", end="")

        else:
            # PAL, determine remaining offsets using arithmetic
            ger_message_table_offset = nes_message_table_end
            # print(f"ger_message_table_offset: {ger_message_table_offset:X}")
            fra_message_table_offset = (nes_message_table_end + staff_message_table_offset) // 2
            # print(f"fra_message_table_offset: {fra_message_table_offset:X}")

            # print(f"nes_message_table_offset: {nes_message_table_offset:X}")
            # print(f"ger_message_table_offset: {ger_message_table_offset:X}")
            # print(f"fra_message_table_offset: {fra_message_table_offset:X}")
            print(f"{nes_message_table_offset:X},{ger_message_table_offset:X},{fra_message_table_offset:X},", end="")

        # print(f"staff_message_table_offset: {staff_message_table_offset:X}")
        # print(f"staff_message_table_end: {staff_message_table_end:X}")
        print(f"{staff_message_table_offset:X},{staff_message_table_end:X}")

        # print(checks)

def findTextTables3(file):
    with open(file, "r+b") as f:
        mm = mmap.mmap(f.fileno(), 0)

        # Look backwards for nes_message_table
        nes_message_table_offset = mm.rfind(NES_FIRST_MESSAGE)
        if nes_message_table_offset == -1:
            return -1

        # Look forwards for end of nes_message_table
        nes_message_table_end = mm.find(MAIN_LAST_MESSAGE, nes_message_table_offset)
        if nes_message_table_end == 0:
            return -1
        nes_message_table_end += 8

        # Look forwards for staff
        staff_message_table_offset = mm.find(STAFF_FIRST_MESSAGE, nes_message_table_end)
        # Look forwards for staff end
        staff_message_table_end = mm.find(MAIN_LAST_MESSAGE, staff_message_table_offset)
        staff_message_table_end += 8

        if nes_message_table_end == staff_message_table_offset:
            # NTSC, look backwards for jpn_message_table
            jpn_message_table_offset = mm.rfind(JPN_FIRST_MESSAGE, nes_message_table_offset)
            
            print(f"nes_message_table_offset: {nes_message_table_offset:X}")
            print(f"jpn_message_table_offset: {jpn_message_table_offset:X}")
            # print(f"{nes_message_table_offset:X},{jpn_message_table_offset:X},", end="")

        else:
            # PAL, determine remaining offsets using arithmetic
            ger_message_table_offset = nes_message_table_end
            fra_message_table_offset = (nes_message_table_end + staff_message_table_offset) // 2

            print(f"nes_message_table_offset: {nes_message_table_offset:X}")
            print(f"ger_message_table_offset: {ger_message_table_offset:X}")
            print(f"fra_message_table_offset: {fra_message_table_offset:X}")
            # print(f"{nes_message_table_offset:X},{ger_message_table_offset:X},{fra_message_table_offset:X},", end="")

        print(f"staff_message_table_offset: {staff_message_table_offset:X}")
        print(f"staff_message_table_end: {staff_message_table_end:X}")
        # print(f"{staff_message_table_offset:X},{staff_message_table_end:X}")


def main():
    description = "Find the text tables from a provided `code` file"
    epilog = ""

    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("code", help="`code` file to search.")
    args = parser.parse_args()

    # findTextTables(args.code)
    findTextTables3(args.code)
    # findTextTablesReverse(args.code)

if __name__ == "__main__":
    main()
