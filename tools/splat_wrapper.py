#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).parent.parent
TOOLS_DIR = ROOT / "tools"
SPLAT_DIR = TOOLS_DIR / "splat"

sys.path.append(str(SPLAT_DIR))

import splat

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("game")
    parser.add_argument("version")
    parser.add_argument("--stdout-only", help="Print all output to stdout", action="store_true")
    parser.add_argument( "--disassemble-all", help="Disasemble matched functions and migrated data", action="store_true")

    args = parser.parse_args()

    config_yaml = f"{args.game}/{args.version}/tables/{args.game}_{args.version}.yaml"

    splat.split.main(
        [config_yaml],
        None,
        False,
        False,
        False,
        args.stdout_only,
        args.disassemble_all,
    )
