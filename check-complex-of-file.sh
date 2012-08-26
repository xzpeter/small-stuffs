#!/bin/bash

# I am using this file to check the complexity of files in the current
# directory (recursively)

# first, find the files I need to check

files=$(find -name "*.c")

function usage() {
    cat <<EOF

This script loop current directory and list all source files in the below format:
NUMBER_LINES	SOURCE_NAME

EOF
}

if [ $# -ne "0" ]; then
    usage
    exit
fi

function checkit() {
    # now checking lines
    file=$1
    lines=$(cat $file | wc -l)
    echo -e "${lines}\t${file}"
}

for file in $files; do
    checkit $file
done | sort -n
