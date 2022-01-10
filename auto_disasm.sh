#! /usr/bin/env bash

if [[ "$#" -ne 1 ]]; then
    echo "Error: exactly one argument required"
    echo "USAGE: $0 GAME"
    echo "Extracts all currently supported files in the passed GAME."
    exit 1
fi

GAME=$1

for file in boot code
do
    echo -e "\nDisassembling ${file} in each version"
    while read version
    do
        echo -e "\n${version}:"
        make GAME=${GAME} VERSION=${version} "${GAME}/${version}/asm/text/${file}/.disasm"
    done < "${GAME}/versions_${GAME}.txt"
done

if [[ ${GAME} == "oot" ]]; then
    for file in n64dd
    do
        echo -e "\nDisassembling ${file} in each n64 version"
        while read version
        do
            echo -e "\n${version}:"
            make GAME=oot VERSION=${version} "oot/${version}/asm/text/${file}/.disasm"    
        done < "oot/n64_versions.txt"
    done
fi

echo -e "\nAll files disassembled"
