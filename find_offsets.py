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
    En_A_Obj_InitVars = data.find(search)
    return struct.unpack(">I",data[En_A_Obj_InitVars + 0x10:En_A_Obj_InitVars + 0x14])[0]

def find_code_data_offset(data, game):
    if game == "mm":
        search = bytes.fromhex("340A0FC0")
    return data.find(search)

def find_code_rodata_offset(data, game):
    if game == "mm":
        search = bytes.fromhex("3F19999A 80")
    return data.find(search)

def find_kaleido_strings(data, game):
    if game == "mm": # possibly unnecessary
        search = b"kaleido_scope"
    return data.find(search)

def find_kaleido_dlftbls(data, game):
    if game == "mm":
        # print(f"{find_code_vram(data, game) + find_kaleido_strings(data, game):08X}")
        search = bytes.fromhex(f"{find_code_vram(data, game) + find_kaleido_strings(data, game):08X}")
        # print(search)
        return data.find(search) - 0x18

def find_actor_dlftbls(data, game):
    if game == "mm":
        search = bytes.fromhex("00000000 00000000 00000000 00000000 00000000 80")
    return data.find(search)

def find_game_dlftbls(data, game):
    if game == "mm":
        search = bytes.fromhex("00000000 00000000 00000000 000000A4 00000000")
    return data.find(search) - 0x20

def find_effect_dlftbls(data, game):
    if game == "mm":
        search = bytes.fromhex("01000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000")
    # return data.find(search)
    return bad_find(data, search, 4) - 0x34

def find_fbdemo_dlftbls(data, game):
    if game == "mm":
        search = bytes.fromhex("0000000C 00000000 80")
    return data.find(search) - 0x18


def main():
    description = ""
    epilog = ""
    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    choices = ["oot", "mm"]
    parser.add_argument("game", help="Game to extract.", choices=choices)
    parser.add_argument("code", help="code file to parse.")
    args = parser.parse_args()

    
    try:
        with open(args.code, 'rb') as f:
            data = f.read()
    except IOError:
        print('Failed to read file ' + args.code)
        sys.exit(1)

    print(f"code VRAM start:    {find_code_vram(data, args.game):X}\n")
    print(f"code data offset:     {find_code_data_offset(data, args.game):X}")
    print(f"code rodata offset:   {find_code_rodata_offset(data, args.game):X}\n")

    print(f"effect table:         {find_effect_dlftbls(data, args.game):X}")
    print(f"actor table:          {find_actor_dlftbls(data, args.game):X}")
    print(f"game table:           {find_game_dlftbls(data, args.game):X}")
    print(f"kaleido table:        {find_kaleido_dlftbls(data, args.game):X}")
    print(f"fbdemo table:         {find_fbdemo_dlftbls(data, args.game):X}")


if __name__ == "__main__":
    main()
