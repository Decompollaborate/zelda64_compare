# Zelda64 version comparison scripts

TODO: write description

N.B. Support for Animal Forest is quite limited at present, but is being actively worked on.

## Setup

- Each ROM you wish to extract for comparison should be named `baserom_{version}.z64`.
- (Optional) Run `fixbaserom.py` for every version just to be sure: the roms are expected to be big-endian.
- Run `make setup GAME={game} VERSION={version}` for every version you wish to compare to extract the baseroms to separate decompressed files, e.g.

  ```bash
  make GAME=MM VERSION=ne0
  ```

  will extract MM's US N64 version (see the bottom of the README.md for the abbreviations this repository uses)

  <!-- - `extract_every_baserom.sh` will try to extract every known version, and ignore the missing ones (This will take a while...). -->

- Run `make GAME={game} VERSION={version}` to disassemble.

## Usage

- If you update a Google sheet, `download_csv.sh` will pull every sheet down.
- Rerunning `make` with the appropriate variables set will re-disassemble with the new symbols.
- To change the files that are extracted, edit the appropriate game's `disasm_list.txt`. By default only a few files are diassembled to save time.

N.B. DnM overlays are not currently supported since the relocation section is separate.

## Comparison scripts

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

The Legend of Zelda: Ocarina of Time

| Abbreviation | Description                                  |
| ------------ | -------------------------------------------- |
| njr          | ner with the language byte changed           |
| ner          | "0.9" prerelease build found in early 2021   |
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

The Legend of Zelda: Majora's Mask

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

### DnM

Doubutsu no Mori AKA Animal Forest. (Not a Zelda title, but shares many systems with the Zelda64 games.)

| Abbreviation | Description             |
| ------------ | ----------------------- |
| jp           | N64 Japanese            |
| cn           | iQue Simplified Chinese |
