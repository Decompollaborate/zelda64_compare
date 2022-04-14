#!/usr/bin/env python3

from __future__ import annotations


ENTRYPOINT = 0x80000400

ActorIDMax = {
    "oot": 0x1D7,
    "mm":  0x2B2,
}

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

bootVramStart = {
    "oot": {
        "NER":      0x80000460,
        "NE0":      0x80000460,
        "NE1":      0x80000460,
        "NP0":      0x80000460,
        "NE2":      0x80000460,
        "NP1":      0x80000460,
        "CJO":      0x80000460,
        "CJM":      0x80000460,
        "CEO":      0x80000460,
        "CEM":      0x80000460,
        "CPOD1":    0x80000460,
        "CPMD":     0x80000460,
        "CPOD2":    0x80000460,
        "CPO":      0x80000460,
        "CPM":      0x80000460,
        "CJC":      0x80000460,
        "IQS":      0x80000450, # iQue likes to be special
        "IQT":      0x80000450,
    },

    "mm": {
        "NJ0":      0xFFFFFF, # TODO: FIX
        "NJ1":      0xFFFFFF, # TODO: FIX
        "NEK":      0xFFFFFF, # TODO: FIX
        "NE0":      0xFFFFFF, # TODO: FIX
        "NP0":      0xFFFFFF, # TODO: FIX
        "NPD":      0xFFFFFF, # TODO: FIX
        "NP1":      0xFFFFFF, # TODO: FIX
        "CE0":      0xFFFFFF, # TODO: FIX
        "CP0":      0xFFFFFF, # TODO: FIX
        "CJ0":      0xFFFFFF, # TODO: FIX
    },
}

bootDataStart = {
    "oot": {
        "NER":      -1,
        "NE0":      -1,
        "NE1":      -1,
        "NP0":      0x62B0,
        "NE2":      0x6310,
        "NP1":      0x62B0,
        "CJO":      0x5C70,
        "CJM":      0x5C70,
        "CEO":      0x5C70,
        "CEM":      0x5C70,
        "CPOD1":    0x8FD0,
        "CPMD":     0x8FD0,
        "CPOD2":    0x8FD0,
        "CPO":      0x5C70,
        "CPM":      0x5C70,
        "CJC":      0x5C70,
        "IQS":      0x98F0,
        "IQT":      0x9380,
    },

    "mm": {
        "NJ0":      0xFFFFFF, # TODO: FIX
        "NJ1":      0xFFFFFF, # TODO: FIX
        "NEK":      0xFFFFFF, # TODO: FIX
        "NE0":      0xFFFFFF, # TODO: FIX
        "NP0":      0xFFFFFF, # TODO: FIX
        "NPD":      0xFFFFFF, # TODO: FIX
        "NP1":      0xFFFFFF, # TODO: FIX
        "CE0":      0xFFFFFF, # TODO: FIX
        "CP0":      0xFFFFFF, # TODO: FIX
        "CJ0":      0xFFFFFF, # TODO: FIX
    },
}

bootRodataStart = {
    "oot": {
        "NER":      0x60F0,
        "NE0":      0x60F0,
        "NE1":      0x60F0,
        "NP0":      0x6610,
        "NE2":      0x6620,
        "NP1":      0x6610,
        "CJO":      0x5F40,
        "CJM":      0x5F40,
        "CEO":      0x5F40,
        "CEM":      0x5F40,
        "CPOD1":    0xAB60,
        "CPMD":     0xAB60,
        "CPOD2":    0xAB60,
        "CPO":      0x5F40,
        "CPM":      0x5F40,
        "CJC":      0x5F40,
        "IQS":      0x9D40,
        "IQT":      0x97F0,
    },

    "mm": {
        "NJ0":      0xFFFFFF, # TODO: FIX
        "NJ1":      0xFFFFFF, # TODO: FIX
        "NEK":      0xFFFFFF, # TODO: FIX
        "NE0":      0xFFFFFF, # TODO: FIX
        "NP0":      0xFFFFFF, # TODO: FIX
        "NPD":      0xFFFFFF, # TODO: FIX
        "NP1":      0xFFFFFF, # TODO: FIX
        "CE0":      0xFFFFFF, # TODO: FIX
        "CP0":      0xFFFFFF, # TODO: FIX
        "CJ0":      0xFFFFFF, # TODO: FIX
    },
}

codeVramStart = {
    "oot": {
        "NER":      0x800110A0,
        "NE0":      0x800110A0,
        "NE1":      0x800110A0,
        "NP0":      0x800116E0,
        "NE2":      0x800116E0,
        "NP1":      0x800116E0,
        "CJO":      0x80010EE0,
        "CJM":      0x80010EE0,
        "CEO":      0x80010EE0,
        "CEM":      0x80010EE0,
        "CPOD1":    0x8001CE60,
        "CPMD":     0x8001CE60,
        "CPOD2":    0x8001CE60,
        "CPO":      0x80010F00,
        "CPM":      0x80010F00,
        "CJC":      0x80010EE0,
        "IQS":      0x80018FA0,
        "IQT":      0x80018A40,
    },

    "mm": {
        "NJ0":      0x800A76A0,
        "NJ1":      0x800A75E0,
        "NEK":      0xFFFFFF, # TODO: FIX
        "NE0":      0x800A5AC0,
        "NP0":      0x800A5D60,
        "NPD":      0xFFFFFF, # TODO: FIX
        "NP1":      0x800A5FE0,
        "CE0":      0x800A6440,
        "CP0":      0x800A65A0,
        "CJ0":      0x800A6420,
    },
}

codeDataStart = {
    "oot": {
        "NER":      0x0D6400,
        "NE0":      0x0D6610,
        "NE1":      0x0D67D0,
        "NP0":      0x0D3F20,
        "NE2":      0x0D6610,
        "NP1":      0x0D3F60,
        "CJO":      0x0D5CE0,
        "CJM":      0x0D5CC0,
        "CEO":      0x0D5CC0,
        "CEM":      0x0D5CA0,
        "CPOD1":    0x0F85E0,
        "CPMD":     0x0F85C0,
        "CPOD2":    0x0F85E0,
        "CPO":      0x0D3620,
        "CPM":      0x0D3600,
        "CJC":      0x0D5CC0,
        "IQS":      0x0D6330,
        "IQT":      0x0D5C10,
    },

    "mm": {
        "NJ0":      0xFE2F0,
        "NJ1":      0xFE5F0,
        "NEK":      0xFFFFFF, # TODO: FIX
        "NE0":      0x104FF0,
        "NP0":      0x801AB5D0 - 0x800A5D60,
        "NPD":      0xFFFFFF, # TODO: FIX
        "NP1":      0x801AB970 - 0x800A5FE0,
        "CE0":      0x801A9510 - 0x800A6440,
        "CP0":      0x801A9F30 - 0x800A65A0,
        "CJ0":      0x801A95B0 - 0x800A6420,
    },
}

codeRodataStart = {
    "oot": {
        "NER":      0x0F4A50,
        "NE0":      0x0F4C60,
        "NE1":      0x0F4E20,
        "NP0":      0x0F2570,
        "NE2":      0x0F4C60,
        "NP1":      0x0F25B0,
        "CJO":      0x0F3E90,
        "CJM":      0x0F3E70,
        "CEO":      0x0F3E70,
        "CEM":      0x0F3E50,
        "CPOD1":    0x117EF0,
        "CPMD":     0x117ED0,
        "CPOD2":    0x117EF0,
        "CPO":      0x0F17D0,
        "CPM":      0x0F17B0,
        "CJC":      0x0F3E70,
        "IQS":      0x0F44C0,
        "IQT":      0x0F3DE0,
    },

    "mm": {
        "NJ0":      0x12EE80,
        "NJ1":      0x801D6730 - 0x800A75E0,
        "NEK":      0xFFFFFF, # TODO: FIX
        "NE0":      0x136330,
        "NP0":      0x801D4380 - 0x800A5D60,
        "NPD":      0xFFFFFF, # TODO: FIX
        "NP1":      0x801D4720 - 0x800A5FE0,
        "CE0":      0x801DB070 - 0x800A6440,
        "CP0":      0x801D2CC0 - 0x800A65A0,
        "CJ0":      0x801DB060 - 0x800A6420,
    },
}
