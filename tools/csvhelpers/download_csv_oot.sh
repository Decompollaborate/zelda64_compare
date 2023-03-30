#! /usr/bin/env bash

set -e

# Run the script from the root of the project
# DIR="$(dirname "$(readlink -f "$0")")"
# cd "$DIR/../.."


## Functions and variables
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=1299953822" -O - | tr -d '\r' > "oot/tables/functions.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=196803778"  -O - | tr -d '\r' > "oot/tables/variables.csv"

## boot
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=10092675"   -O - | tr -d '\r' > "oot/tables/boot.text.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=141056684"  -O - | tr -d '\r' > "oot/tables/boot.data.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=85246168"   -O - | tr -d '\r' > "oot/tables/boot.rodata.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=34933535"   -O - | tr -d '\r' > "oot/tables/boot.bss.csv"

## iQue boot (yes, this is necessary because of file reorderings and I hate it)
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=566575037"  -O - | tr -d '\r' > "oot/tables/iQue.boot.text.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=870131088"  -O - | tr -d '\r' > "oot/tables/iQue.boot.data.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=735109002"  -O - | tr -d '\r' > "oot/tables/iQue.boot.rodata.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=2062718156" -O - | tr -d '\r' > "oot/tables/iQue.boot.bss.csv"

## code
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=204902945"  -O - | tr -d '\r' > "oot/tables/code.text.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=428775213"  -O - | tr -d '\r' > "oot/tables/code.data.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=1062318484" -O - | tr -d '\r' > "oot/tables/code.rodata.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=1375291344" -O - | tr -d '\r' > "oot/tables/code.bss.csv"

## n64dd
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=959352547"  -O - | tr -d '\r' > "oot/tables/n64dd.text.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=1208054228" -O - | tr -d '\r' > "oot/tables/n64dd.data.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=2035868832" -O - | tr -d '\r' > "oot/tables/n64dd.rodata.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=1720384253" -O - | tr -d '\r' > "oot/tables/n64dd.bss.csv"


## ovl_file_choose
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=2117679852"  -O - | tr -d '\r' > "oot/tables/ovl_file_choose.text.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=879682381"   -O - | tr -d '\r' > "oot/tables/ovl_file_choose.data.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=344185256"   -O - | tr -d '\r' > "oot/tables/ovl_file_choose.rodata.csv"
wget "https://docs.google.com/spreadsheets/d/17yPD3DqqH5lZeR7c_QmJfgxWgVyYkGgTLZoKcvLTwtw/export?format=csv&gid=702866421"   -O - | tr -d '\r' > "oot/tables/ovl_file_choose.bss.csv"
