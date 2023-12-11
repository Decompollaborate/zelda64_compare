#!/usr/bin/env python3

from __future__ import annotations

import argparse
import dataclasses
from pathlib import Path
import spimdisasm
from typing import TextIO

from mips.MipsSplitEntry import readSegmentSplitsFromSheetCsv, SplitEntry

@dataclasses.dataclass
class DmaEntry:
    name: str
    virt_start: int
    virt_end: int
    phys_start: int
    phys_end: int
    splits: list[SplitEntry]
    section_order: list[str] = dataclasses.field(default_factory=list)

def readDmaInfo(game: str, version: str) -> list[DmaEntry]:
    dma_info: list[DmaEntry] = []

    dma_addresses_path = Path(f"{game}/{version}/tables/dma_addresses.csv")
    dma_addresses = spimdisasm.common.Utils.readCsv(dma_addresses_path)

    csvNamePrefix = ""
    if version in {"iqs", "iqt"}:
        csvNamePrefix = "iQue."

    for segment_name, virt_start_str, virt_end_str, phys_start_str, phys_end_str in dma_addresses:
        virt_start = int(virt_start_str, 16)
        virt_end = int(virt_end_str, 16)
        phys_start = int(phys_start_str, 16)
        phys_end = int(phys_end_str, 16)

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

        dma_entry = DmaEntry(segment_name, virt_start, virt_end, phys_start, phys_end, segment_splits)
        if segment_name == "makerom":
            dma_entry.section_order = [".data", ".text", ".rodata", ".bss"]
            if len(segment_splits) == 0:
                entry = SplitEntry(version, "rom_header", 0x000000, 0x40, 0x80000000)
                entry.section = ".data"
                segment_splits.append(entry)

                entry = SplitEntry(version, "ipl3", 0x000040, 0x1000-0x40, 0x80000040)
                entry.section = ".databin"
                segment_splits.append(entry)

                entry = SplitEntry(version, "entry", 0x001000, 0x60, 0x80001000) # TODO: proper vram
                entry.section = ".hasm"
                segment_splits.append(entry)

        dma_info.append(dma_entry)

    return dma_info


def write_header(f: TextIO, game: str, version: str):
    f.write(f"""\
name: zelda (zelda, TODO)
# sha1: TODO
options:
  basename: zelda
  base_path: oot/cpmd
  target_path: ../oot_cpmd_uncompressed.z64
  elf_path: build/oot_cpmd.elf
  ld_script_path: linker_scripts/oot_cpmd.ld
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


def write_segment(f: TextIO, dma_entry: DmaEntry):
    finished_sections = {
        "asm": False,
        "data": False,
        "rodata": False,
        "bss": False,
    }

    f.write(f"""
- name: {dma_entry.name}
  start: 0x{dma_entry.virt_start:06X}
""")
    if len(dma_entry.splits) == 0:
        f.write(f"""\
  type: databin
""")
        return

    f.write(f"""\
  type: code
  vram: 0x{dma_entry.splits[0].vram:08X}
""")
    if len(dma_entry.section_order) > 0:
        f.write(f"""\
  section_order: {dma_entry.section_order}
""")
    f.write(f"""\
  subsegments:
""")
    lastSection = ""
    linker_section = ""
    first_bss = True
    for split in dma_entry.splits:
        section = split.splatSection()

        rom_offset = dma_entry.virt_start + split.offset
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

def write_segments(f: TextIO, game: str, version: str, dma_addresses: list[DmaEntry]):
    assert len(dma_addresses) > 0

    f.write(f"""\
segments:
""")

    for dma_entry in dma_addresses:
        write_segment(f, dma_entry)

    f.write(f"\n- [0x{dma_addresses[-1].virt_end:06X}]\n")

GAME = "oot"
VERSION = "cpmd"

dma_info = readDmaInfo(GAME, VERSION)

path = Path(f"{GAME}/{VERSION}/tables/{VERSION}.yaml")
with path.open("w") as f:
    write_header(f, GAME, VERSION)
    write_segments(f, GAME, VERSION, dma_info)
