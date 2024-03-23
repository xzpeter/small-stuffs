#!/usr/bin/env bash
#
# This script helps to move ROMs from one dir to another.  Could be useful
# if you have a backup of ROMs then you want to move it to a newly built
# system.
#
# You may want to modify src_to_dst, which is the rule to convert a src
# subdir name to dst.

prog_name=$0

usage()
{
    echo "$prog_name <src_rom_dir> <dst_rom_dir>"
    echo
    echo "Copy ROM files from src to dest dir, matching archs"
    exit 0
}

src_to_dst()
{
    tr '[:upper:]' '[:lower:]' | \
        sed 's/^md$/megadrive/' | \
        sed 's/^ps$/psx/' | \
        sed 's/^sfc/snes/'
}

echo_err()
{
    echo "ERROR: $@"
    exit -1
}

if [[ $# -lt 2 ]]; then
    usage
fi

src_dir=$1
dst_dir=$2

if [[ ! -d "$src_dir" ]]; then
    echo_err "Source dir $src_dir is not a directory"
fi

if [[ ! -d "$dst_dir" ]]; then
    echo_err "Destination dir $dst_dir is not a directory"
fi

src_subs=$(ls $src_dir)
for arch in $src_subs; do
    dst_arch=$(echo $arch | src_to_dst)
    if ls $dst_dir/$dst_arch &> /dev/null; then
        echo "Found arch $arch..."
        echo "Copying files for $arch..."
        rsync -r --progress $src_dir/$arch/* $dst_dir/$dst_arch
    else
        echo "Didn't find arch $dst_arch"
    fi
done
