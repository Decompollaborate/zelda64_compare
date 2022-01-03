#!/usr/bin/python3

from __future__ import annotations

import argparse
import os
import sys
import struct
from multiprocessing import Pool, cpu_count, Manager
from typing import Dict, List
import zlib


ROM_FILE_NAME = 'baserom.z64'
ROM_FILE_NAME_V = '{}_{}.z64'
FILE_TABLE_OFFSET = {
    "OOT": {
        "NTSC 0.9":     0x07430, # a.k.a. NTSC 1.0 RC
        "NTSC 1.0":     0x07430,
        "NTSC 1.1":     0x07430,
        "PAL 1.0":      0x07950,
        "NTSC 1.2":     0x07960,
        "PAL 1.1":      0x07950,
        "JP GC":        0x07170,
        "JP MQ":        0x07170,
        "USA GC":       0x07170,
        "USA MQ":       0x07170,
        "PAL GC DBG1":  0x12F70,
        "PAL MQ DBG":   0x12F70,
        "PAL GC DBG2":  0x12F70,
        "PAL GC":       0x07170,
        "PAL MQ":       0x07170,
        "JP GC CE":     0x07170, # Zelda collection
        "IQUE CN":      0x0B7A0,
        "IQUE TW":      0x0B240,
        "GATEWAY":      0x0AC80, # fake
    },

    "MM": {
        "NJ0":    0x1C110,
        "NJ1":    0x1C050,
        "NEK":    0x1AB50,
        "NE0":    0x1A500,
        "NP0":    0x1A650,
        "NPD":    0x24F60,
        "NP1":    0x1A8D0,
        "CE0":    0x1AE90,
        "CP0":    0x1AE90,
        "CJ0":    0x1AE90,
    },
}
FILE_TABLE_OFFSET["OOT"]["NTSC J 0.9"]   = FILE_TABLE_OFFSET["OOT"]["NTSC 0.9"]
FILE_TABLE_OFFSET["OOT"]["NTSC J 1.0"]   = FILE_TABLE_OFFSET["OOT"]["NTSC 1.0"]
FILE_TABLE_OFFSET["OOT"]["NTSC J 1.1"]   = FILE_TABLE_OFFSET["OOT"]["NTSC 1.1"]
FILE_TABLE_OFFSET["OOT"]["NTSC J 1.2"]   = FILE_TABLE_OFFSET["OOT"]["NTSC 1.2"]
FILE_TABLE_OFFSET["OOT"]["PAL WII 1.1"]  = FILE_TABLE_OFFSET["OOT"]["PAL 1.1"]

FILE_NAMES: Dict[str, Dict[str, List[str] | None]] = {
    "OOT": {
        "NTSC 0.9":     None,
        "NTSC 1.0":     None,
        "NTSC 1.1":     None,
        "PAL 1.0":      None,
        "NTSC 1.2":     None,
        "PAL 1.1":      None,
        "JP GC":        None,
        "JP MQ":        None,
        "USA GC":       None,
        "USA MQ":       None,
        "PAL GC DBG1":  None,
        "PAL GC DBG2":  None,
        "PAL MQ DBG":   None,
        "PAL GC":       None,
        "PAL MQ":       None,
        "JP GC CE":     None, # Zelda collector's edition
        "IQUE CN":      None,
        "IQUE TW":      None,
        "GATEWAY":      None, # fake
    },

    "MM": {
        "NJ0":    None,
        "NJ1":    None,
        "NEK":    None,
        "NE0":    None,
        "NP0":    None,
        "NPD":    None,
        "NP1":    None,
        "CE0":    None,
        "CP0":    None,
        "CJ0":    None,
    },
}
FILE_NAMES["OOT"]["NTSC J 0.9"]  = FILE_NAMES["OOT"]["NTSC 0.9"]
FILE_NAMES["OOT"]["NTSC J 1.0"]  = FILE_NAMES["OOT"]["NTSC 1.0"]
FILE_NAMES["OOT"]["NTSC J 1.1"]  = FILE_NAMES["OOT"]["NTSC 1.1"]
FILE_NAMES["OOT"]["NTSC J 1.2"]  = FILE_NAMES["OOT"]["NTSC 1.2"]
FILE_NAMES["OOT"]["PAL WII 1.1"] = FILE_NAMES["OOT"]["PAL 1.1"]

romData: bytes = None
Edition = "" # "pal_mq"
Version = "" # "PAL MQ"


def readFile(filepath):
    with open(filepath) as f:
        return [x.strip() for x in f.readlines()]

def readFilelists():
    FILE_NAMES["OOT"]["PAL MQ DBG"] = readFile("filelists/filelist_pal_mq_dbg.txt")
    FILE_NAMES["OOT"]["PAL MQ"] = readFile("filelists/filelist_pal_mq.txt")
    FILE_NAMES["OOT"]["USA MQ"] = readFile("filelists/filelist_usa_mq.txt")
    FILE_NAMES["OOT"]["NTSC 1.0"] = readFile("filelists/filelist_ntsc_1.0.txt")
    FILE_NAMES["OOT"]["PAL 1.0"] = readFile("filelists/filelist_pal_1.0.txt")
    FILE_NAMES["OOT"]["JP GC CE"] = readFile("filelists/filelist_jp_gc_ce.txt")
    FILE_NAMES["OOT"]["IQUE CN"] = readFile("filelists/filelist_ique_cn.txt")

    FILE_NAMES["OOT"]["JP MQ"] = FILE_NAMES["OOT"]["USA MQ"]

    FILE_NAMES["OOT"]["USA GC"] = FILE_NAMES["OOT"]["JP GC CE"]
    FILE_NAMES["OOT"]["JP GC"]  = FILE_NAMES["OOT"]["USA GC"]
    FILE_NAMES["OOT"]["PAL GC"] = FILE_NAMES["OOT"]["PAL MQ"]

    FILE_NAMES["OOT"]["PAL 1.1"] = FILE_NAMES["OOT"]["PAL 1.0"]

    FILE_NAMES["OOT"]["PAL GC DBG1"] = FILE_NAMES["OOT"]["PAL MQ DBG"]
    FILE_NAMES["OOT"]["PAL GC DBG2"] = FILE_NAMES["OOT"]["PAL MQ DBG"]

    FILE_NAMES["OOT"]["IQUE TW"] = FILE_NAMES["OOT"]["IQUE CN"]

    FILE_NAMES["OOT"]["NTSC 0.9"] = FILE_NAMES["OOT"]["NTSC 1.0"]
    FILE_NAMES["OOT"]["NTSC 1.1"] = FILE_NAMES["OOT"]["NTSC 1.0"]
    FILE_NAMES["OOT"]["NTSC 1.2"] = FILE_NAMES["OOT"]["NTSC 1.0"]

    FILE_NAMES["OOT"]["NTSC J 0.9"]  = FILE_NAMES["OOT"]["NTSC 0.9"]
    FILE_NAMES["OOT"]["NTSC J 1.0"]  = FILE_NAMES["OOT"]["NTSC 1.0"]
    FILE_NAMES["OOT"]["NTSC J 1.1"]  = FILE_NAMES["OOT"]["NTSC 1.1"]
    FILE_NAMES["OOT"]["NTSC J 1.2"]  = FILE_NAMES["OOT"]["NTSC 1.2"]
    FILE_NAMES["OOT"]["PAL WII 1.1"] = FILE_NAMES["OOT"]["PAL 1.1"]

    FILE_NAMES["OOT"]["GATEWAY"] = FILE_NAMES["OOT"]["IQUE CN"]

    # MM
    FILE_NAMES["MM"]["NJ0"] = readFile("mm/filelists/filelist_mm_jp_1.0.txt")
    FILE_NAMES["MM"]["NEK"] = readFile("mm/filelists/filelist_mm_usa_demo.txt")
    FILE_NAMES["MM"]["NE0"] = readFile("mm/filelists/filelist_mm_usa.txt")
    FILE_NAMES["MM"]["NPD"] = readFile("mm/filelists/filelist_mm_pal_dbg.txt")
    FILE_NAMES["MM"]["CE0"] = readFile("mm/filelists/filelist_mm_usa_gc.txt")
    FILE_NAMES["MM"]["CP0"] = readFile("mm/filelists/filelist_mm_pal_gc.txt")
    FILE_NAMES["MM"]["CJ0"] = readFile("mm/filelists/filelist_mm_jp_gc.txt")

    FILE_NAMES["MM"]["NJ1"]  = FILE_NAMES["MM"]["NJ0"]
    FILE_NAMES["MM"]["NP0"] = FILE_NAMES["MM"]["NPD"]
    FILE_NAMES["MM"]["NP1"] = FILE_NAMES["MM"]["NP0"]

def initialize_worker(rom_data: bytes, dmaTable: dict):
    global romData
    global globalDmaTable
    romData = rom_data
    globalDmaTable = dmaTable

def read_uint32_be(offset):
    return struct.unpack('>I', romData[offset:offset+4])[0]

def write_output_file(name, offset, size):
    try:
        with open(name, 'wb') as f:
            f.write(romData[offset:offset+size])
    except IOError:
        print('failed to write file ' + name)
        sys.exit(1)


def decompressZlib(data: bytearray) -> bytearray:
    decomp = zlib.decompressobj(-zlib.MAX_WBITS)
    output = bytearray()
    output.extend(decomp.decompress(data))
    while decomp.unconsumed_tail:
        output.extend(decomp.decompress(decomp.unconsumed_tail))
    output.extend(decomp.flush())
    return output

def writeBytearrayToFile(filepath: str, array_of_bytes: bytearray):
    with open(filepath, mode="wb") as f:
       f.write(array_of_bytes)

def readFileAsBytearray(filepath: str) -> bytearray:
    if not os.path.exists(filepath):
        return bytearray(0)
    with open(filepath, mode="rb") as f:
        return bytearray(f.read())


def ExtractFunc(i):
    versionName = FILE_NAMES[Game][Version][i]
    if versionName == "":
        print(f"Skipping {i} because it doesn't have a name.")
        return
    filename = os.path.join(Basedir, Edition, "baserom", versionName)
    entryOffset = FILE_TABLE_OFFSET[Game][Version] + 16 * i

    virtStart = read_uint32_be(entryOffset + 0)
    virtEnd   = read_uint32_be(entryOffset + 4)
    physStart = read_uint32_be(entryOffset + 8)
    physEnd   = read_uint32_be(entryOffset + 12)

    if physStart == 0xFFFFFFFF and physEnd == 0xFFFFFFFF: # file deleted
        if (virtEnd - virtStart) == 0:
            return
        physStart = virtStart
        physEnd = 0
        compressed = False
        size = virtEnd - virtStart
    if physEnd == 0:  # uncompressed
        compressed = False
        size = virtEnd - virtStart
    else:             # compressed
        compressed = True
        size = physEnd - physStart

    globalDmaTable[versionName].append(virtStart)
    globalDmaTable[versionName].append(virtEnd)
    globalDmaTable[versionName].append(physStart)
    globalDmaTable[versionName].append(physEnd)

    print('Extracting ' + filename + " (0x%08X, 0x%08X)" % (virtStart, virtEnd))
    write_output_file(filename, physStart, size)
    if compressed:
        # print(f"decompressing {filename}")
        if Edition in ("ique_cn", "ique_tw"):
            data = readFileAsBytearray(filename)
            decompressed = decompressZlib(data)
            writeBytearrayToFile(filename, decompressed)
        else:
            exit_code = os.system('tools/yaz0 -d ' + filename + ' ' + filename)
            if exit_code != 0:
                pass
                #os.remove(filename)
                # exit(exit_code)

#####################################################################

def printBuildData(rom_data: bytes):
    buildDataOffset = FILE_TABLE_OFFSET[Game][Version] - 16*3
    buildTeam = ""
    i = 0
    while rom_data[buildDataOffset + i] != 0:
        buildTeam += chr(rom_data[buildDataOffset + i])
        i += 1

    while rom_data[buildDataOffset + i] == 0:
        i += 1

    buildDate = ""
    while rom_data[buildDataOffset + i] != 0:
        buildDate += chr(rom_data[buildDataOffset + i])
        i += 1

    i += 1

    buildMakeOption = ""
    while rom_data[buildDataOffset + i] != 0:
        buildMakeOption += chr(rom_data[buildDataOffset + i])
        i += 1

    print("========================================")
    print(f"| Build team:   {buildTeam}".ljust(39) + "|")
    print(f"| Build date:   {buildDate}".ljust(39) + "|")
    #print(f"| Make Option:  {buildMakeOption}".ljust(39) + "|")
    print("========================================")

def extract_rom(j):
    print("Reading filelists...")
    readFilelists()

    file_names_table = FILE_NAMES[Game][Version]
    if file_names_table is None:
        print(f"'{Edition}' is not supported yet because the filelist is missing.")
        sys.exit(2)

    try:
        os.makedirs(os.path.join(Basedir, Edition, "baserom"))
    except:
        pass

    filename = os.path.join(Basedir, ROM_FILE_NAME_V.format(Basedir, Edition))
    if not os.path.exists(filename):
        print(f"{filename} not found. Defaulting to {ROM_FILE_NAME}")
        filename = ROM_FILE_NAME

    # read baserom data
    try:
        with open(filename, 'rb') as f:
            rom_data = f.read()
    except IOError:
        print('Failed to read file ' + filename)
        sys.exit(1)

    manager = Manager()
    dmaTable = manager.dict()
    for name in file_names_table:
        dmaTable[name] = manager.list()

    # extract files
    if j:
        num_cores = cpu_count()
        print("Extracting rom with " + str(num_cores) + " CPU cores.")
        with Pool(num_cores, initialize_worker, (rom_data, dmaTable)) as p:
            p.map(ExtractFunc, range(len(file_names_table)))
    else:
        initialize_worker(rom_data, dmaTable)
        for i in range(len(file_names_table)):
            ExtractFunc(i)

    printBuildData(rom_data)


    try:
        os.makedirs(os.path.join(Basedir, Edition, "tables"))
    except:
        pass

    filetable = os.path.join(Basedir, Edition, "tables", "dma_addresses.txt")
    print(f"Creating {filetable}")
    with open(filetable, "w") as f:
        for filename, data in dmaTable.items():
            f.write(",".join([filename] + list(map(str, data))) + "\n")

def main():
    description = "Extracts files from the rom. Will try to read the rom 'version.z64', or 'baserom.z64' if that doesn't exist."

    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    choices = ["oot", "mm"]
    parser.add_argument("game", help="Game to extract.", choices=choices, default="oot")
    # choices = [x.lower().replace(" ", "_") for x in FILE_TABLE_OFFSET["OOT"]]
    parser.add_argument("edition", help="Version of the game to extract.", default="pal_mq_dbg")
    parser.add_argument("-j", help="Enables multiprocessing.", action="store_true")
    parser.add_argument("-b", "--basedir", help="folder in which to work")
    args = parser.parse_args()

    global Basedir
    global Game
    global Edition
    global Version

    Basedir = args.game
    Game    = args.game.upper()
    Edition = args.edition
    Version = Edition.upper().replace("_", " ")

    extract_rom(args.j)

if __name__ == "__main__":
    main()
