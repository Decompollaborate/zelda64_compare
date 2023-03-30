#! /usr/bin/env bash

set -e

# Run the script from the root of the project
# DIR="$(dirname "$(readlink -f "$0")")"
# cd "$DIR/../.."


## Functions and variables
wget "https://docs.google.com/spreadsheets/d/12cKSs6fX211H_ufGUUSIjdPmlMbt3ZLyW71GLpAm0_4/export?format=csv&gid=1063621067" -O - | tr -d '\r' > "mm/tables/functions.csv"
wget "https://docs.google.com/spreadsheets/d/12cKSs6fX211H_ufGUUSIjdPmlMbt3ZLyW71GLpAm0_4/export?format=csv&gid=1570476402" -O - | tr -d '\r' > "mm/tables/variables.csv"

## boot
wget "https://docs.google.com/spreadsheets/d/12cKSs6fX211H_ufGUUSIjdPmlMbt3ZLyW71GLpAm0_4/export?format=csv&gid=269020656"  -O - | tr -d '\r' > "mm/tables/boot.text.csv"
wget "https://docs.google.com/spreadsheets/d/12cKSs6fX211H_ufGUUSIjdPmlMbt3ZLyW71GLpAm0_4/export?format=csv&gid=680636738"  -O - | tr -d '\r' > "mm/tables/boot.data.csv"
wget "https://docs.google.com/spreadsheets/d/12cKSs6fX211H_ufGUUSIjdPmlMbt3ZLyW71GLpAm0_4/export?format=csv&gid=1260565170" -O - | tr -d '\r' > "mm/tables/boot.rodata.csv"
wget "https://docs.google.com/spreadsheets/d/12cKSs6fX211H_ufGUUSIjdPmlMbt3ZLyW71GLpAm0_4/export?format=csv&gid=1589823056" -O - | tr -d '\r' > "mm/tables/boot.bss.csv"

## code
wget "https://docs.google.com/spreadsheets/d/12cKSs6fX211H_ufGUUSIjdPmlMbt3ZLyW71GLpAm0_4/export?format=csv&gid=0"          -O - | tr -d '\r' > "mm/tables/code.text.csv"
wget "https://docs.google.com/spreadsheets/d/12cKSs6fX211H_ufGUUSIjdPmlMbt3ZLyW71GLpAm0_4/export?format=csv&gid=1298997316" -O - | tr -d '\r' > "mm/tables/code.data.csv"
wget "https://docs.google.com/spreadsheets/d/12cKSs6fX211H_ufGUUSIjdPmlMbt3ZLyW71GLpAm0_4/export?format=csv&gid=1712837674" -O - | tr -d '\r' > "mm/tables/code.rodata.csv"
wget "https://docs.google.com/spreadsheets/d/12cKSs6fX211H_ufGUUSIjdPmlMbt3ZLyW71GLpAm0_4/export?format=csv&gid=1266090971" -O - | tr -d '\r' > "mm/tables/code.bss.csv"
