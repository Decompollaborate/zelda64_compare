#! /usr/bin/env bash

set -e

# # Run the script from the root of the project
# DIR="$(dirname "$(readlink -f "$0")")"
# cd "$DIR/../.."


## File adresses
# jp
wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=0"          -O - | tr -d '\r' > "dnm/jp/tables/file_addresses.csv"

## Variables
wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=219617635"  -O - | tr -d '\r' > "dnm/tables/variables.csv"

## Functions
wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=467726846"  -O - | tr -d '\r' > "dnm/tables/boot_functions.csv"
wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=2064898020" -O - | tr -d '\r' > "dnm/tables/code_functions.csv"
wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=105420436"  -O - | tr -d '\r' > "dnm/tables/gamestate_functions.csv"
# Mix the different functions csvs into one
cat "dnm/tables/boot_functions.csv" > "dnm/tables/functions.csv"
echo >> "dnm/tables/functions.csv" # newline
tail -n +3 "dnm/tables/code_functions.csv" >> "dnm/tables/functions.csv"
echo >> "dnm/tables/functions.csv" # newline
tail -n +3 "dnm/tables/gamestate_functions.csv" >> "dnm/tables/functions.csv"

## makerom
wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=1355718882" -O - | tr -d '\r' > "dnm/tables/makerom.text.csv"

## boot
wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=725463820"  -O - | tr -d '\r' > "dnm/tables/boot.text.csv"
# wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=" -O - | tr -d '\r' > "dnm/tables/boot.data.csv"
# wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=" -O - | tr -d '\r' > "dnm/tables/boot.rodata.csv"
# wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=" -O - | tr -d '\r' > "dnm/tables/boot.bss.csv"

## code
wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=1399719350" -O - | tr -d '\r' > "dnm/tables/code.text.csv"
# wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=" -O - | tr -d '\r' > "dnm/tables/code.data.csv"
# wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=" -O - | tr -d '\r' > "dnm/tables/code.rodata.csv"
# wget "https://docs.google.com/spreadsheets/d/17WZXsAATDgXXSBBVEOc_zT-QJDkD72vaGjZ5YyG1a_Y/export?format=csv&gid=" -O - | tr -d '\r' > "dnm/tables/code.bss.csv"
