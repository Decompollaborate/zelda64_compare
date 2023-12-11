#!/usr/bin/env python3

from __future__ import annotations

import argparse
import dataclasses
from pathlib import Path
import spimdisasm
from typing import TextIO

from mips.MipsSplitEntry import readSegmentSplitsFromSheetCsv, SplitEntry
from mips.ZeldaTables import getFileAddresses

@dataclasses.dataclass
class FileInfo:
    name: str
    virt_start: int
    virt_end: int
    splits: list[SplitEntry]
    section_order: list[str] = dataclasses.field(default_factory=list)
    vram: int|None = None

def readDmaInfo(game: str, version: str) -> list[FileInfo]:
    segments_info: list[FileInfo] = []

    file_addresses_path = Path(f"{game}/{version}/tables/file_addresses.csv")
    file_addresses = getFileAddresses(file_addresses_path)

    csvNamePrefix = ""
    if version in {"iqs", "iqt"}:
        csvNamePrefix = "iQue."

    for segment_name, entry in file_addresses.items():
        csv_list: list[tuple[str, Path]] = []

        # Check if a csv with all the sections mixed exists
        split_csv_path = Path(f"{game}/tables/{csvNamePrefix}{segment_name}.csv")
        if not split_csv_path.exists():
            split_csv_path = Path(f"{game}/tables/{segment_name}.csv")
        csv_list = [("", split_csv_path)]

        # If it doesn't exist, default to one file per section
        if not split_csv_path.exists():
            sections = [".text", ".data", ".rodata", ".bss"]
            csv_list = [(sect, Path(f"{game}/tables/{segment_name}{sect}.csv")) for sect in sections]

        segment_splits_per_version = readSegmentSplitsFromSheetCsv(csv_list)
        segment_splits = segment_splits_per_version.get(version, [])

        info_entry = FileInfo(segment_name, entry.vromStart, entry.vromEnd, segment_splits)
        if entry.vramStart > 0:
            info_entry.vram = entry.vramStart
        if segment_name == "makerom":
            info_entry.section_order = [".data", ".text", ".rodata", ".bss"]
            if len(info_entry.splits) == 0:
                entry = SplitEntry(version, "rom_header", 0x000000, 0x40, 0x80000000)
                entry.section = ".data"
                info_entry.splits.append(entry)

                entry = SplitEntry(version, "ipl3", 0x000040, 0x1000-0x40, 0x80000040)
                entry.section = ".databin"
                info_entry.splits.append(entry)

                entry = SplitEntry(version, "entry", 0x001000, 0x60, 0x80001000) # TODO: proper vram
                entry.section = ".hasm"
                info_entry.splits.append(entry)

        if segment_name.startswith("ovl_") and len(info_entry.splits) == 0:
            pass

        segments_info.append(info_entry)

    return segments_info


def write_header(f: TextIO, game: str, version: str):
    f.write(f"""\
name: zelda (zelda, TODO)
# sha1: TODO
options:
  basename: zelda
  base_path: {game}/{version}
  target_path: ../{game}_{version}_uncompressed.z64
  elf_path: build/{game}_{version}.elf
  ld_script_path: linker_scripts/{game}_{version}.ld
  compiler: IDO
  find_file_boundaries: True
  header_encoding: ASCII
  platform: n64
  undefined_funcs_auto_path: linker_scripts/auto/undefined_funcs_auto.ld
  undefined_syms_auto_path: linker_scripts/auto/undefined_syms_auto.ld
  symbol_addrs_path:
    - tables/functions.txt
    - tables/variables.txt

  auto_all_sections: [".text", ".data", ".rodata", ".bss"]

  ld_dependencies: True

  asm_path: asm
  src_path: src
  build_path: build
  asset_path: bin
  extensions_path: tools/splat_ext
  mips_abi_float_regs: o32
  do_c_func_detection: True
  o_as_suffix: True
  gfx_ucode: f3dex2
  mnemonic_ljust: 12
  rom_address_padding: True
  dump_symbols: True
  asm_inc_header: ""
  use_legacy_include_asm: False
  create_asm_dependencies: True
  string_encoding: EUC-JP
  data_string_encoding: EUC-JP
  rodata_string_guesser_level: 2
  asm_function_macro: glabel
  # asm_function_alt_macro: alabel
  # asm_end_label: endlabel
  asm_jtbl_label_macro: jlabel
  asm_data_macro: dlabel
  include_macro_inc: False
  libultra_symbols: True
  ique_symbols: True
  hardware_regs: True

""")


def write_segment(f: TextIO, segmment_entry: FileInfo):
    finished_sections = {
        "asm": False,
        "data": False,
        "rodata": False,
        "bss": False,
    }

    f.write(f"""
- name: {segmment_entry.name}
  start: 0x{segmment_entry.virt_start:06X}
""")
    if len(segmment_entry.splits) == 0:
        f.write(f"""\
  type: databin
""")
        if segmment_entry.vram is not None:
            f.write(f"""\
  vram: 0x{segmment_entry.vram:08X}
""")
        return

    f.write(f"""\
  type: code
  vram: 0x{segmment_entry.vram if segmment_entry.vram is not None else segmment_entry.splits[0].vram:08X}
""")
    if len(segmment_entry.section_order) > 0:
        f.write(f"""\
  section_order: {segmment_entry.section_order}
""")
    f.write(f"""\
  subsegments:
""")
    lastSection = ""
    linker_section = ""
    first_bss = True
    for split in segmment_entry.splits:
        section = split.splatSection()

        rom_offset = segmment_entry.virt_start + split.offset
        if section != lastSection and not finished_sections.get(section, False):
            finished_sections[lastSection] = True
            linker_section = split.section

        filename = split.filename
        if filename == ".end":
            break
        if filename == "[PADDING]":
            filename = f"padding_{rom_offset:06X}"

        if section == "bss":
            if first_bss:
                first_bss = False
                f.write(f"""\
  - {{ start: 0x{rom_offset:06X}, type: {section}, vram: 0x{split.vram:08X}, name: {filename} }}
""")
            else:
                f.write(f"""\
  - {{ type: {section}, vram: 0x{split.vram:08X}, name: {filename} }}
""")
        elif finished_sections.get(section, False):
            f.write(f"""\
  - {{ start: 0x{rom_offset:06X}, type: {section}, name: {filename}, linker_section_order: {linker_section} }}
""")
        else:
            f.write(f"""\
  - [0x{rom_offset:06X}, {section}, {filename}]
""")
        lastSection = section

def write_segments(f: TextIO, game: str, version: str, segments_info: list[FileInfo]):
    assert len(segments_info) > 0

    f.write(f"""\
segments:
""")

    for segmment_entry in segments_info:
        write_segment(f, segmment_entry)

    print(segments_info[-1])
    f.write(f"\n- [0x{segments_info[-1].virt_end:06X}]\n")

GAME = "oot"
VERSION = "cpmd"

segments_info = readDmaInfo(GAME, VERSION)

path = Path(f"{GAME}/{VERSION}/tables/{VERSION}.yaml")
with path.open("w") as f:
    write_header(f, GAME, VERSION)
    write_segments(f, GAME, VERSION, segments_info)
