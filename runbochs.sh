#!/bin/bash

# this script will try to find one bochs configuration file under the
# current directory, and then load this file with the bochs emulator
# quietly 

file=$(ls *.bxrc | sed -n '1p')

if [ "$file" == "" ]; then
    cat <<EOF
    Cannot find any bochs configuration file under current
    directory. Quitting.
EOF
    exit 0
fi

echo "trying to load bochs with configure file: $file"
