#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
import os
import struct
from typing import Callable

from construct_spec import printf


@dataclass # very cursed
class control_code_info: # cursed but necessary
    name: str
    arg_size: int
    format: Callable


# Formatting functions

def format_default(name, arg):
    if arg != None:
        return "\" {}(\"\\x{:X}\") \"".format(name, int.from_bytes(arg, 'big'))
    else:
        return "\" {} \"".format(name)

def format_break(name, arg):
    if arg != None:
        return "\" {}({}) \"".format(name, arg)
    else:
        return "\" \n{} \n    \"".format(name)

def format_newline(name, arg):
        return "\\n\"\n    \""

def format_end(name, arg):
        return "\" {}".format(name)

# cheat for jpn by throwing away the top byte
colors = {
    0x00 : "DEFAULT",
    0x01 : "RED",
    0x02 : "ADJUSTABLE",
    0x03 : "BLUE",
    0x04 : "LIGHTBLUE",
    0x05 : "PURPLE",
    0x06 : "YELLOW",
    0x07 : "BLACK",
}

def format_color(name, arg):
    try:
        return "\" {}({}) \"".format(name, colors[int.from_bytes(arg, 'big') & 0xF])
    except :
        print(arg)
        return "ERR"

highscores = {
    0x00 : "HS_HORSE_ARCHERY",
    0x01 : "HS_POE_POINTS",
    0x02 : "HS_LARGEST_FISH",
    0x03 : "HS_HORSE_RACE",
    0x04 : "HS_MARATHON",
    0x06 : "HS_DAMPE_RACE",
}

def format_highscore(name, arg):
    return "\" {}({}) \"".format(name, highscores[int.from_bytes(arg, 'big')])

### nes-specific

nes_special_chs = {
    0x7F: '‾',
    0x80: 'À',
    0x81: 'î',
    0x82: 'Â',
    0x83: 'Ä',
    0x84: 'Ç',
    0x85: 'È',
    0x86: 'É',
    0x87: 'Ê',
    0x88: 'Ë',
    0x89: 'Ï',
    0x8A: 'Ô',
    0x8B: 'Ö',
    0x8C: 'Ù',
    0x8D: 'Û',
    0x8E: 'Ü',
    0x8F: 'ß',
    0x90: 'à',
    0x91: 'á',
    0x92: 'â',
    0x93: 'ä',
    0x94: 'ç',
    0x95: 'è',
    0x96: 'é',
    0x97: 'ê',
    0x98: 'ë',
    0x99: 'ï',
    0x9A: 'ô',
    0x9B: 'ö',
    0x9C: 'ù',
    0x9D: 'û',
    0x9E: 'ü',
    0x9F: '[A]',
    0xA0: '[B]',
    0xA1: '[C]',
    0xA2: '[L]',
    0xA3: '[R]',
    0xA4: '[Z]',
    0xA5: '[C-Up]',
    0xA6: '[C-Down]',
    0xA7: '[C-Left]',
    0xA8: '[C-Right]',
    0xA9: '▼',
    0xAA: '[Control-Pad]',
    0xAB: '[D-Pad]',
}

nes_control_codes = {
    b"\x01": control_code_info("NEWLINE", 0, format_newline),
    b"\x02": control_code_info("END", 0, format_end),
    b"\x04": control_code_info("BOX_BREAK", 0, format_default),
    b"\x05": control_code_info("COLOR", 1, format_color),
    b"\x06": control_code_info("SHIFT", 1, format_default),
    b"\x07": control_code_info("TEXTID", 2, format_default),
    b"\x08": control_code_info("QUICKTEXT_ENABLE", 0, format_default),
    b"\x09": control_code_info("QUICKTEXT_DISABLE", 0, format_default),
    b"\x0A": control_code_info("PERSISTENT", 0, format_default),
    b"\x0B": control_code_info("EVENT", 0, format_default),
    b"\x0C": control_code_info("BOX_BREAK_DELAYED", 1, format_default),
    b"\x0D": control_code_info("AWAIT_BUTTON_PRESS", 0, format_default), # Used?
    b"\x0E": control_code_info("FADE", 1, format_default),
    b"\x0F": control_code_info("NAME", 0, format_default),
    b"\x10": control_code_info("OCARINA", 0, format_default),
    b"\x11": control_code_info("FADE2", 0, format_default), # Used?
    b"\x12": control_code_info("SFX", 2, format_default),
    b"\x13": control_code_info("ITEM_ICON", 1, format_default),
    b"\x14": control_code_info("TEXT_SPEED", 1, format_default),
    b"\x15": control_code_info("BACKGROUND", 3, format_default),
    b"\x16": control_code_info("MARATHON_TIME", 0, format_default),
    b"\x17": control_code_info("RACE_TIME", 0, format_default),
    b"\x18": control_code_info("POINTS", 0, format_default),
    b"\x19": control_code_info("TOKENS", 0, format_default),
    b"\x1A": control_code_info("UNSKIPPABLE", 0, format_default),
    b"\x1B": control_code_info("TWO_CHOICE", 0, format_default),
    b"\x1C": control_code_info("THREE_CHOICE", 0, format_default),
    b"\x1D": control_code_info("FISH_INFO", 0, format_default),
    b"\x1E": control_code_info("HIGHSCORE", 1, format_highscore),
    b"\x1F": control_code_info("TIME", 0, format_default),
}

def nes_decode_ch(ch):
    if ch[0] in nes_special_chs:
        return nes_special_chs[ch[0]]
    else:
        try:
            return ch.decode("ascii")
        except UnicodeDecodeError:
            return "\\x{:X}".format(ch[0])


def decode_msg_jpn(bytes):
    msg_len = len(bytes)
    i = 0
    buf = ["    \""] # this is a list, so appending and += are the same
    while i < msg_len:
        ch = bytes[i:i+2]

        if ch in jpn_control_codes:
            info = jpn_control_codes[ch]
            if info.arg_size > 0:
                i += 2
                arg = bytes[ i : i + info.arg_size ]
                i += info.arg_size
                buf += info.format(info.name, arg)
                continue
            else:
                buf += info.format(info.name, None)
        else:
            if int(ch[0]) == 0x83:
                if ch[1] in jpn_special_chs:
                    buf += jpn_special_chs[ch[1]]
                else:
                    buf += ch.decode("shift-jis")
            else:
                try:
                    buf += ch.decode("shift-jis")
                except UnicodeDecodeError:
                    buf += "\\x{:X}\\x{:X}".format(ch[0],ch[1])
        
        i += 2
        
    # buf += "\" "
    msg = "".join(buf)
    msg = msg.replace("\"\" ","")
    msg = msg.replace("\"\x00\x00\" ","")
    print(msg, end="")

### jpn-specific

jpn_special_chs = {
    0x9F: '[A]',
    0xA0: '[B]',
    0xA1: '[C]',
    0xA2: '[L]',
    0xA3: '[R]',
    0xA4: '[Z]',
    0xA5: '[C-Up]',
    0xA6: '[C-Down]',
    0xA7: '[C-Left]',
    0xA8: '[C-Right]',
    0xA9: '▼',
    0xAA: '[Control-Pad]',
    0xAB: '[D-Pad]',
}

jpn_control_codes = {
    b"\x00\x0A": control_code_info("NEWLINE", 0, format_newline),
    b"\x81\x70": control_code_info("END", 0, format_end),
    b"\x81\xA5": control_code_info("BOX_BREAK", 0, format_default),
    b"\x00\x0B": control_code_info("COLOR", 1, format_color),
    b"\x86\xC7": control_code_info("SHIFT", 1, format_default),
    b"\x81\xCB": control_code_info("TEXTID", 1, format_default),
    b"\x81\x89": control_code_info("QUICKTEXT_ENABLE", 0, format_default),
    b"\x81\x8A": control_code_info("QUICKTEXT_DISABLE", 0, format_default),
    b"\x86\xC8": control_code_info("PERSISTENT", 0, format_default),
    b"\x81\x9F": control_code_info("EVENT", 0, format_default),
    b"\x81\xA3": control_code_info("BOX_BREAK_DELAYED", 1, format_default),
    # b"\x": "AWAIT_BUTTON_PRESS", # Used?
    b"\x81\x9E": control_code_info("FADE", 1, format_default),
    b"\x87\x4F": control_code_info("NAME", 0, format_default),
    b"\x81\xF0": control_code_info("OCARINA", 0, format_default),
    # b"\x": "FADE2", # Used?
    b"\x81\xF3": control_code_info("SFX", 1, format_default),
    b"\x81\x9A": control_code_info("ITEM_ICON", 1, format_default),
    b"\x86\xC9": control_code_info("TEXT_SPEED", 1, format_default),
    b"\x86\xB3": control_code_info("BACKGROUND", 2, format_default),
    b"\x87\x91": control_code_info("MARATHON_TIME", 0, format_default),
    b"\x87\x92": control_code_info("RACE_TIME", 0, format_default),
    b"\x87\x9B": control_code_info("POINTS", 0, format_default),
    b"\x86\xA3": control_code_info("TOKENS", 0, format_default),
    b"\x81\x99": control_code_info("UNSKIPPABLE", 0, format_default),
    b"\x81\xBC": control_code_info("TWO_CHOICE", 0, format_default),
    b"\x81\xB8": control_code_info("THREE_CHOICE", 0, format_default),
    b"\x86\xA4": control_code_info("FISH_INFO", 0, format_default),
    b"\x86\x9F": control_code_info("HIGHSCORE", 1, format_highscore),
    b"\x81\xA1": control_code_info("TIME", 0, format_default),
}

def jpn_decode_ch(ch):
    if int(ch[0]) == 0x83:
        if ch[1] in jpn_special_chs:
            return jpn_special_chs[ch[1]]
        else:
            return ch.decode("shift-jis")
    else:
        try:
            return ch.decode("shift-jis")
        except UnicodeDecodeError:
            return "\\x{:X}\\x{:X}".format(ch[0],ch[1])


@dataclass
class langInfo:
    ch_width: int
    control_codes: dict
    special_chs: dict
    ch_decode: Callable # for the non-control chs

languageInfo = {
    "jpn": langInfo(2, jpn_control_codes, jpn_special_chs, jpn_decode_ch),
    "nes": langInfo(1, nes_control_codes, nes_special_chs, nes_decode_ch)
}

def decode_msg(bytes, lang):
    
    ch_width = languageInfo[lang].ch_width
    control_codes = languageInfo[lang].control_codes
    msg_len = len(bytes)
    i = 0
    buf = ["    \""] # this is a list, so appending and += are the same
    while i < msg_len:
        ch = bytes[ i : i + ch_width]

        if ch in control_codes:
            info = control_codes[ch]
            if info.arg_size > 0:
                i += ch_width
                arg = bytes[ i : i + info.arg_size * ch_width ]
                i += info.arg_size * ch_width
                buf += info.format(info.name, arg)
                continue
            else:
                buf += info.format(info.name, None)
        else:
            buf += languageInfo[lang].ch_decode(ch)
        
        i += ch_width
        
    # buf += "\" "
    msg = "".join(buf)
    msg = msg.replace("\"\" ","")
    msg = msg.replace("\"\x00\x00\" ","")
    print(msg, end="")

def read_data(file, start, end):
        
    with open(file, "rb") as f:
        f.seek(start, os.SEEK_SET)
        if end == 0:
            return f.read()
        else:
            return f.read(end - start)

def main():
    description = ""
    epilog = ""

    parser = argparse.ArgumentParser(description=description, epilog=epilog, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("file", help="file to read.")
    parser.add_argument("-s", "--start", help="Start of chunk to read.")
    parser.add_argument("-e", "--end", help="End of chunk to read.")
    
    args = parser.parse_args()


    start = int(args.start, 0) if args.start else 0
    end = int(args.end, 0) if args.end else 0

    print(f"{start:X},{end:X}")

    data = read_data(args.file, start, end)
    decode_msg_jpn(data)


if __name__ == "__main__":
    main()
