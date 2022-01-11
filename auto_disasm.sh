#! /usr/bin/env bash

FILES="boot code"

print_usage () {
    echo "USAGE: $1 GAME [VERSION]+"
    echo "Extracts all currently supported files in the passed GAME for all versions, or any VERSIONs passed."
}

disassemble_file () {
    echo -e "\nDisassembling ${file} in ${version}:"
    make GAME=$1 VERSION=$2 "$1/$2/asm/text/$3/.disasm"
}


if [[ "$#" -eq 0 ]]; then
    print_usage $0
    exit 1
fi

GAME_OPTIONS="oot mm"
GAME=$1
if [[ "${GAME_OPTIONS}" != *"${GAME}"* ]]; then
    echo "Error: GAME argument not found, must be one of 'oot' or 'mm' "
    exit 1
fi


if [[ "$#" -ge 2 ]]; then
    GAME_VERSIONS=$(cat "${GAME}/versions_${GAME}.txt")

    for version in "${@:2}"
    do
        if [[ "GAME_VERSIONS" =~ "${version}" ]]; then
            echo "Error: VERSION not found, must be one of:"
            echo -e "$GAME_VERSIONS"
            continue
        fi

        for file in ${FILES}
        do
            disassemble_file "${GAME}" "${version}" "${file}"
        done

        if [[ "${GAME}" != "oot" ]]; then
            continue
        fi

        N64_VERSIONS=$(cat "${GAME}/n64_versions.txt")
        for file in n64dd
        do
            if [[ "${N64_VERSIONS}" =~ "${version}" ]]; then
                disassemble_file "${GAME}" "${version}" "${file}"
            fi
        done

    done
    exit 0
fi

for file in ${FILES}
do
    echo -e "\n    Disassembling ${file} in each version"
    while read version
    do
        disassemble_file "${GAME}" "${version}" "${file}"
    done < "${GAME}/versions_${GAME}.txt"
done

if [[ ${GAME} == "oot" ]]; then
    for file in n64dd
    do
        echo -e "\n    Disassembling ${file} in each n64 version"
        while read version
        do
            disassemble_file "${GAME}" "${version}" "${file}"
        done < "oot/n64_versions.txt"
    done
fi

echo -e "\nAll files disassembled"
