#!/usr/bin/python3

import argparse
import os
import struct

# First message entry in JPN text table
JPN_FIRST_MESSAGE = bytes.fromhex("0001230008000000")
# First message entry in NES text table
NES_FIRST_MESSAGE = bytes.fromhex("0001230007000000")
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
        s = f.read()
        nes_message_table_offset = s.find(NES_FIRST_MESSAGE)
        if nes_message_table_offset == -1:
            nes_message_table_offset = 0
            print("nes_message_table not found")
        else:
            nes_message_table_offset += jpn_message_table_offset
            print(f"nes_message_table_offset: {nes_message_table_offset:X}")
        
        f.seek(nes_message_table_offset, os.SEEK_SET)
        s = f.read()

        if jpn_message_table_offset == 0:
            ger_message_table_offset = s.find(MAIN_LAST_MESSAGE)
            if ger_message_table_offset == -1:
                ger_message_table_offset = 0
                print("ger_message_table not found")
            else:
                ger_message_table_offset += 8 + nes_message_table_offset
                print(f"ger_message_table_offset: {ger_message_table_offset:X}")

            f.seek(ger_message_table_offset, os.SEEK_SET)
            s = f.read()
            fra_message_table_offset = s.find(SUB_LAST_MESSAGE)
            if fra_message_table_offset == -1:
                fra_message_table_offset = 0
                print("fra_message_table not found")
            else:
                fra_message_table_offset += 4 + ger_message_table_offset
                print(f"fra_message_table_offset: {fra_message_table_offset:X}")

            f.seek(fra_message_table_offset, os.SEEK_SET)
            s = f.read()
            staff_message_table_offset = s.find(SUB_LAST_MESSAGE) 
            staff_message_table_offset += 4 + fra_message_table_offset
        
        else:
            staff_message_table_offset = s.find(MAIN_LAST_MESSAGE)
            staff_message_table_offset += 8 + nes_message_table_offset

        print(f"staff_message_table_offset: {staff_message_table_offset:X}")
        f.seek(staff_message_table_offset, os.SEEK_SET)
        s = f.read()
        staff_message_table_end = s.find(MAIN_LAST_MESSAGE) 
        staff_message_table_end += 8 + staff_message_table_offset
        print(f"staff_message_table_end: {staff_message_table_end:X}")







def main():
    description = "Find the text tables from a provided `code` file"
    epilog = ""

    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("code", help="`code` file to search.")
    args = parser.parse_args()

    findTextTables(args.code)


if __name__ == "__main__":
    main()
