# OoT versions comparisons scripts

TODO: write description

## Setup

- Each ROM should be named `baserom_{version}.z64`.
- (Optional) Run `fixbaserom.py` for every version just to be sure.
- Run `extract_baserom.py {version}` for every version you have.

  ```bash
  ./extract_baserom.py pal_mq_dbg -j
  ```

  - `extract_every_baserom.sh` will try to extract every known version, and ignore the missing ones (This will take a while...).

## Usage

TODO

## Version abbreviations

Because OoT has over 20 different versions, and MM 10, it's necessary to have short abbreviations for each version when comparing. The first two letters are mostly from Nintendo's designations, for media
- `N` is cartridge
- `C` is disc
and for regions
- `J` is Japan
- `E` is America
- `P` is PAL (Australia as well as Europe, at least in this case)

The following tables give the more common name/description of each version:

### OoT

| Abbreviation | Description                                  |
| ------------ | -------------------------------------------- |
| njr          | ner with the language byte changed           |
| ner          | "0.9" build found in early 2021              |
| nj0          | N64 Japanese 1.0                             |
| ne0          | N64 American 1.0                             |
| nj1          | N64 Japanese 1.1                             |
| ne1          | N64 American 1.1                             |
| np0          | N64 PAL 1.0                                  |
| nj2          | N64 Japanese 1.2                             |
| ne2          | N64 American 1.2                             |
| np1          | N64 PAL 1.1                                  |
| cjo          | GC Japanese original                         |
| cjm          | GC Japanese Master Quest                     |
| ceo          | GC American original                         |
| cem          | GC American Master Quest                     |
| cpod1        | GC PAL original Debug, earlier build date    |
| cpod2        | GC PAL original Debug, later build date      |
| cpmd         | GC PAL Master Quest Debug                    |
| cpo          | GC PAL original                              |
| cpm          | GC PAL Master Quest                          |
| cjc          | GC Japanese Zelda Collection                 |
| iqs          | iQue (Simplified Chinese), released in China |
| iqt          | iQue (Traditional Chinese), unreleased       |
| pal_wii_1.1  | Wii Virtual Console PAL. Romhack of np1.     |

(`ne0`, `ne1`, `ne2` are just `nj0`, `nj1`, `nj2` with the language byte changed.)

### MM

| Abbreviation | Description                              |
| ------------ | ---------------------------------------- |
| nj0          | N64 Japanese 1.0                         |
| nj1          | N64 Japanese 1.1                         |
| nek          | N64 American Kiosk Demo                  |
| ne0          | N64 American 1.0                         |
| np0          | N64 PAL 1.0                              |
| npd          | N64 PAL Debug                            |
| np1          | N64 PAL 1.1                              |
| cjo          | GC Japanese                              |
| ceo          | GC American                              |
| cpo          | GC PAL                                   |
| pal_wii_1.1  | Wii Virtual Console PAL. Romhack of np1. |
