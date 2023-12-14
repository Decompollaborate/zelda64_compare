#!/usr/bin/env python3

from __future__ import annotations

import argparse
import dataclasses
from pathlib import Path
import spimdisasm

from mips.ZeldaTables import getFileAddresses

def write(f, thingy):
    print(thingy, end="")
    f.write(thingy)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("game")
    parser.add_argument("version")
    args = parser.parse_args()

    game: str = args.game
    version: str = args.version

    file_addresses_path = Path(f"{game}/{version}/tables/file_addresses.csv")
    file_addresses = getFileAddresses(file_addresses_path)
    assert len(file_addresses) > 0

    rom_data = Path(f"{game}/{game}_{version}_uncompressed.z64").read_bytes()

    ovl_sections_path = Path(f"{game}/{version}/tables/ovl_sections.csv")
    with ovl_sections_path.open("w") as f:
        write(f, f"name,text size,data size,rodata size,ovl size,bss size\n")

        prev_segment_name = ""
        for segment_name, segment_entry in file_addresses.items():
            if (game in {"oot", "mm"} and segment_name.startswith("ovl_")) or (game in {"dnm"} and prev_segment_name.startswith("ovl_")):
                name = segment_name
                segment = rom_data[segment_entry.vromStart:segment_entry.vromEnd]

                seekup = spimdisasm.common.Utils.bytesToWords(segment[-4:])[0]

                # Remove non reloc stuff
                segment = segment[-seekup:]

                text_size, data_size, rodata_size, bss_size = spimdisasm.common.Utils.bytesToWords(segment, 0, 4*4)
                ovl_size = len(segment)

                if game in {"dnm"}:
                    name = prev_segment_name
                    ovl_size = 0

                write(f, f"{name},0x{text_size:X},0x{data_size:X},0x{rodata_size:X},0x{ovl_size:X},0x{bss_size:X}\n")
            prev_segment_name = segment_name

if __name__ == "__main__":
    main()
