#!/usr/bin/env python3

import sys
import csv
import argparse
import struct
import find_offsets



ActorOverlayEntrySize = 0x20
ActorIDCount = {
    "oot": 0x1D7,
    "mm":  0x2B2,
}

EffectSsOverlayEntrySize = 0x1C
EffectSsIDCount = {
    "oot": 0x25,
    "mm": 0x27,
}

GamestateOverlayEntrySize = 0x30
GamestateIDCount = {
    "oot": 6,
    "mm" : 7,
}

KaleidoOverlayEntrySize = 0x1C


def bytesToBEWords(array_of_bytes):
    words = len(array_of_bytes)//4
    big_endian_format = f">{words}I"
    return list(struct.unpack_from(big_endian_format, array_of_bytes, 0))


def printf(fmt, *args, **kwargs):
    print(fmt.format(*args), end="", **kwargs)

def fprintf(file, *args, **kwargs):
    printf(*args, file=file, **kwargs)

def constructActorTable(data, game):
    tableOffset = find_offsets.find_actor_dlftbls(data, game)
    actorTable = []
    i = 0
    while i < ActorIDCount[game]:
        curOffset = tableOffset + ActorOverlayEntrySize * i
        entry = struct.unpack(">IIII", data[curOffset:curOffset + 0x10 ])
        actorTable.append(entry)
        i += 1
    return actorTable

def constructEffectSsTable(data, game):
    tableOffset = find_offsets.find_effect_dlftbls(data, game)
    effectTable = []
    i = 0
    while i < EffectSsIDCount[game]:
        curOffset = tableOffset + EffectSsOverlayEntrySize * i
        entry = struct.unpack(">IIII", data[curOffset:curOffset + 0x10 ])
        effectTable.append(entry)
        i += 1
    return effectTable

def constructGamestateTable(data, game):
    tableOffset = find_offsets.find_game_dlftbls(data, game)
    gameTable = []
    i = 0
    while i < GamestateIDCount[game]:
        curOffset = tableOffset + GamestateOverlayEntrySize * i
        entry = struct.unpack(">IIII", data[curOffset + 4 : curOffset + 0x10 + 4 ])
        gameTable.append(entry)
        i += 1
    return gameTable

def constructKaleidoTable(data, game):
    tableOffset = find_offsets.find_kaleido_dlftbls(data, game)
    kaleidoTable = []
    i = 0
    while i < 2:
        curOffset = tableOffset + KaleidoOverlayEntrySize * i
        entry = struct.unpack(">IIII", data[curOffset + 4 : curOffset + 0x10 + 4 ])
        kaleidoTable.append(entry)
        i += 1
    return kaleidoTable

def constructMapMarkDataTable(data, game):
    tableOffset = find_offsets.find_map_mark_data_dlftbl(data, game)
    mapMarkDataTable = []
    i = 0
    while i < 1:
        curOffset = tableOffset + i * 0x8
        entry = struct.unpack(">IIII", data[curOffset + 4 : curOffset + 0x10 + 4 ])
        mapMarkDataTable.append(entry)
        i += 1
    return mapMarkDataTable

def constructOverlayTable(code, game):
    try:
        with open(code, 'rb') as f:
            data = f.read()
    except IOError:
        print('Failed to read file ' + code)
        sys.exit(1)

    overlayTable = []
    overlayTable.extend(constructActorTable(data, game))
    overlayTable.extend(constructEffectSsTable(data, game))
    overlayTable.extend(constructGamestateTable(data, game))
    overlayTable.extend(constructKaleidoTable(data, game))
    overlayTable.extend(constructMapMarkDataTable(data, game))

    overlayTable.sort()
    return overlayTable

def main():
    description = "Construct a basic spec from dmadata"

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("game", help="Game to use")
    parser.add_argument("code", help="code file to read")
    # parser.add_argument("--outFile", help="File to write to", default=sys.stdout)
    args = parser.parse_args()


    # for entry in constructKaleidoTable(data, args.game):
    #     for number in entry:
    #         print(f"{number:X},",end="")
    #     print("")
    
    overlayTable = constructOverlayTable(args.code, args.game)

    for entry in overlayTable:
        for number in entry:
            print(f"{number:X},",end="")
        print("")


if __name__ == "__main__":
    main()

