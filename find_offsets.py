#!/usr/bin/python3

import os
import sys
import argparse
import struct

def bad_find(data, search, align):
    index = 0
    while index <= len(data) - len(search):
        if data[index:index + len(search)] == search:
            return index
        index += align
    return -1

def find_code_vram(data, game):
    if game == "mm": # possibly unnecessary
        search = bytes.fromhex("00260600 00000009 00010000 00000194")
    else:
        search = bytes.fromhex("00390600 00000010 00010000 0000")

    En_A_Obj_InitVars = data.find(search)
    # Find aligned address, since for OoT there is a setup function with 2 or 3 instructions first
    return struct.unpack(">I",data[En_A_Obj_InitVars + 0x10:En_A_Obj_InitVars + 0x14])[0] & ~0xF

def find_code_data_offset(data, game):
    # Start of the rsp data
    search = bytes.fromhex("340A0FC0")
    return data.find(search)

def find_code_rodata_offset(data, game):
    if game == "mm":
        # First rodata in EnItem00
        search = bytes.fromhex("3F19999A 80")
        return data.find(search)
    else:
        # For debug
        search = b"../z_en_a_keep.c"
        EnAKeepRodataStart = data.find(search)
        if EnAKeepRodataStart != -1:
            return EnAKeepRodataStart
        else:
            # First float in EnItem00
            search = bytes.fromhex("BF19999A")
            index = data.find(search)
            # look backwards until find bytes not part of a jumptable
            while data[index - 4] == 0x80:
                index -= 4
            return index

def find_kaleido_strings(data, game):
    # \0 included to remove filename results
    search = b"kaleido_scope\0"
    return data.find(search)

def find_kaleido_dlftbls(data, game):
    # print(f"{find_code_vram(data, game) + find_kaleido_strings(data, game):08X}")
    search = bytes.fromhex(f"{find_code_vram(data, game) + find_kaleido_strings(data, game):08X}")
    # print(search)
    return data.find(search) - 0x18

def find_actor_dlftbls(data, game):
    # Searches for Player's internal actor entry, which is the first entry in the table.
    search = bytes.fromhex("00000000 00000000 00000000 00000000 00000000 80")
    return data.find(search)

def find_game_dlftbls(data, game):
    # 0xA4 is the size of a gameState, in particular, TitleSetup
    search = bytes.fromhex("00000000 00000000 00000000 000000A4 00000000")
    return data.find(search) - 0x20

def find_effect_dlftbls(data, game):
    # This is an unset effect, have to look backwards for the start
    search = bytes.fromhex("01000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000")
    if game == "mm":
        return bad_find(data, search, 4) - 0x34
    else:
        return bad_find(data, search, 4) - 0xDC

# Only OoT has this
def find_map_mark_data_dlftbl(data, game):
    search = bytes.fromhex("00000400 00000400 00000000")
    return data.find(search) + 0x8

# Only MM has this
def find_fbdemo_dlftbls(data, game):
    search = bytes.fromhex("0000000C 00000000 80")
    return data.find(search) - 0x18


def main():
    description = "Finds the VRAM of the start of code and the offsets of various sections and dlftbls within it."
    epilog = ""
    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    choices = ["oot", "mm"]
    parser.add_argument("game", help="Game to extract.", choices=choices)
    parser.add_argument("code", help="code file to parse.")
    parser.add_argument("--csv", help="Output in CSV format.", action="store_true")
    parser.add_argument("--headers", help="Print CSV headers in CSV mode.", action="store_true")
    args = parser.parse_args()


    
    try:
        with open(args.code, 'rb') as f:
            data = f.read()
    except IOError:
        print('Failed to read file ' + args.code)
        sys.exit(1)

    if args.csv:
        if args.headers:
            print("code_vram_start,code_data_offset,code_rodata_offset,effect_dlftbl,actor_dlftbl,game_dlftbl,kaleido_dlftbl,fbdemo_dlftbl")
        print(f"{find_code_vram(data, args.game):X}", end="")
        print(f",{find_code_data_offset(data, args.game):06X}", end="")
        print(f",{find_code_rodata_offset(data, args.game):06X}", end="")

        print(f",{find_effect_dlftbls(data, args.game):06X}", end="")
        print(f",{find_actor_dlftbls(data, args.game):06X}", end="")
        print(f",{find_game_dlftbls(data, args.game):06X}", end="")
        print(f",{find_kaleido_dlftbls(data, args.game):06X}", end="")

        if args.game == "oot":
           print(f",{find_map_mark_data_dlftbl(data, args.game):06X}", end="")

        if args.game == "mm":
           print(f",{find_fbdemo_dlftbls(data, args.game):06X}", end="")

        print("")

    else:
        print(f"code VRAM start:       {find_code_vram(data, args.game):X}\n")
        print(f"code data offset:        {find_code_data_offset(data, args.game):06X}")
        print(f"code rodata offset:      {find_code_rodata_offset(data, args.game):06X}\n")

        print(f"effectSs table:          {find_effect_dlftbls(data, args.game):06X}")
        print(f"actor table:             {find_actor_dlftbls(data, args.game):06X}")
        print(f"game table:              {find_game_dlftbls(data, args.game):06X}")
        print(f"kaleido table:           {find_kaleido_dlftbls(data, args.game):06X}")
        if args.game == "oot":
            print(f"map_mark_data table:     {find_map_mark_data_dlftbl(data, args.game):06X}")
        if args.game == "mm":
            print(f"fbdemo table:            {find_fbdemo_dlftbls(data, args.game):06X}")


if __name__ == "__main__":
    main()
