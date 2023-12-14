#!/usr/bin/env python3

from __future__ import annotations


# The offset of the overlay table in file `code`.
offset_ActorOverlayTable = {
    "oot": {
        "NER":      0x0D7280,
        "NE0":      0x0D7490,
        "NE1":      0x0D7650,
        "NP0":      0x0D4D80,
        "NE2":      0x0D7490,
        "NP1":      0x0D4DE0,
        "CJO":      0x0D6B60,
        "CJM":      0x0D6B40,
        "CEO":      0x0D6B40,
        "CEM":      0x0D6B20,
        "CPOD1":    0x0F9460,
        "CPMD":     0x0F9440,
        "CPOD2":    0x0F9460,
        "CPO":      0x0D44A0,
        "CPM":      0x0D4480,
        "CJC":      0x0D6B40,
        "IQS":      0x0D7180,
        "IQT":      0x0D6AA0,
    },

    "mm": {
        "NJ0":      0xFFFFFF, # TODO: FIX
        "NJ1":      0xFFFFFF, # TODO: FIX
        "NEK":      0xFFFFFF, # TODO: FIX
        "NE0":      0x109510,
        "NP0":      0xFFFFFF, # TODO: FIX
        "NPD":      0xFFFFFF, # TODO: FIX
        "NP1":      0xFFFFFF, # TODO: FIX
        "CE0":      0xFFFFFF, # TODO: FIX
        "CP0":      0xFFFFFF, # TODO: FIX
        "CJ0":      0xFFFFFF, # TODO: FIX
    },
}
