#!/bin/bash

prog_name=$(basename $0)

usage ()
{
        cat <<EOF
usage: $prog_name <params>

same as: find <params> -name "*.[ch]" >> cscope.files
EOF
        exit 0
}

if [[ -z "$1" ]]; then
        usage
fi

find $@ -name "*.[ch]" | tee -a cscope.files
