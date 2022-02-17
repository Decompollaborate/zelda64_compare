#!/usr/bin/env python3

import argparse
from dataclasses import dataclass
import os
import struct
from typing import Callable


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

colors = {
    0x0C00 : "DEFAULT",
    0x0C01 : "RED",
    0x0C02 : "ADJUSTABLE",
    0x0C03 : "BLUE",
    0x0C04 : "LIGHTBLUE",
    0x0C05 : "PURPLE",
    0x0C06 : "YELLOW",
    0x0C07 : "BLACK",
}

def format_color(name, arg):
    return "\" {}({}) \"".format(name, colors[int.from_bytes(arg, 'big')])

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


# Special characters conversion
special_chars = {
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

control_codes_jpn = {
    b"\x00\x0A": control_code_info("NEWLINE", 0, format_newline),
    b"\x81\x70": control_code_info("END", 0, format_end),
    b"\x81\xA5": control_code_info("BOX_BREAK", 0, format_default),
    b"\x00\x0B": control_code_info("COLOR", 2, format_color),
    b"\x86\xC7": control_code_info("SHIFT", 2, format_default),
    b"\x81\xCB": control_code_info("TEXTID", 2, format_default),
    b"\x81\x89": control_code_info("QUICKTEXT_ENABLE", 0, format_default),
    b"\x81\x8A": control_code_info("QUICKTEXT_DISABLE", 0, format_default),
    b"\x86\xC8": control_code_info("PERSISTENT", 0, format_default),
    b"\x81\x9F": control_code_info("EVENT", 0, format_default),
    b"\x81\xA3": control_code_info("BOX_BREAK_DELAYED", 2, format_default),
    # b"\x": "AWAIT_BUTTON_PRESS", # Used?
    b"\x81\x9E": control_code_info("FADE", 2, format_default),
    b"\x87\x4F": control_code_info("NAME", 0, format_default),
    b"\x81\xF0": control_code_info("OCARINA", 0, format_default),
    # b"\x": "FADE2", # Used?
    b"\x81\xF3": control_code_info("SFX", 2, format_default),
    b"\x81\x9A": control_code_info("ITEM_ICON", 2, format_default),
    b"\x86\xC9": control_code_info("TEXT_SPEED", 2, format_default),
    b"\x86\xB3": control_code_info("BACKGROUND", 4, format_default),
    b"\x87\x91": control_code_info("MARATHON_TIME", 0, format_default),
    b"\x87\x92": control_code_info("RACE_TIME", 0, format_default),
    b"\x87\x9B": control_code_info("POINTS", 0, format_default),
    b"\x86\xA3": control_code_info("TOKENS", 0, format_default),
    b"\x81\x99": control_code_info("UNSKIPPABLE", 0, format_default),
    b"\x81\xBC": control_code_info("TWO_CHOICE", 0, format_default),
    b"\x81\xB8": control_code_info("THREE_CHOICE", 0, format_default),
    b"\x86\xA4": control_code_info("FISH_INFO", 0, format_default),
    b"\x86\x9F": control_code_info("HIGHSCORE", 2, format_highscore),
    b"\x81\xA1": control_code_info("TIME", 0, format_default),
}

def decode_msg_jpn(bytes):
    msg_len = len(bytes)
    i = 0
    buf = ["    \""] # this is a list, so appending and += are the same
    while i < msg_len:
        ch = bytes[i:i+2]

        if ch in control_codes_jpn:
            info = control_codes_jpn[ch]
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
                if ch[1] in special_chars:
                    buf += special_chars[ch[1]]
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
