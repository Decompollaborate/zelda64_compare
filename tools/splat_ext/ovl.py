#!/usr/bin/env python3

from typing import Optional

from segtypes.n64.segment import N64Segment
from segtypes.common.data import CommonSegData


class N64SegOvl(N64Segment, CommonSegData):
    @staticmethod
    def is_data() -> bool:
        return False

    def get_linker_section(self) -> str:
        return ".ovl"

    def get_section_flags(self) -> Optional[str]:
        return "a"

