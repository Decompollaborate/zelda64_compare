#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import spimdisasm
from typing import TextIO


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


def write_segment(f: TextIO, dma_address_info: list[str]):
    name, virt_start_str, virt_end_str, phys_start_str, phys_end_str = dma_address_info
    virt_start = int(virt_start_str, 16)


    if name == "makerom":
        f.write(f"""
- name: makerom
  type: code
  start: 0x000000
  vram: 0x80000000
  section_order: [.data, .text, .rodata, .bss]
  subsegments:
  - [0x000000, data, rom_header]
  - [0x000040, databin, ipl3]
  - [0x001000, hasm, entry]
""")
        return

    if name in {"boot"} and False:
        f.write(f"""
- name: {name}
  type: code
  start: 0x{virt_start:06X}
  vram: 0x80000000
""")
        return

    f.write(f"""
- name: {name}
  type: bin
  start: 0x{virt_start:06X}
""")

def write_segments(f: TextIO, game: str, version: str, dma_addresses: list[list[str]]):
    assert len(dma_addresses) > 0
    assert dma_addresses[0][0] == "makerom"

    f.write(f"""\
segments:
""")

    for dma_address_info in dma_addresses:
        write_segment(f, dma_address_info)

    rom_end = int(dma_addresses[-1][2], 16)
    f.write(f"\n- [0x{rom_end:06X}]\n")

GAME = "oot"
VERSION = "cpmd"

dma_addresses_path = Path(f"{GAME}/{VERSION}/tables/dma_addresses.csv")
dma_addresses = spimdisasm.common.Utils.readCsv(dma_addresses_path)


path = Path(f"{GAME}/{VERSION}/tables/{VERSION}.yaml")
with path.open("w") as f:
    write_header(f, GAME, VERSION)
    write_segments(f, GAME, VERSION, dma_addresses)
