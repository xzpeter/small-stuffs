#!/bin/bash

# generate and update cscope files

function simple {
	find $PWD -name "*.c" -o -name "*.h" -o -name "*.cpp" > cscope.files
	cscope -bqk
}

function kernel {
    LNX=/usr/src/linux-source-3.2.0
    TARGET=/home/xz/tags/linux-source-3.2.0
    cd /
    find  $LNX                                                                \
	-path "$LNX/arch/*" ! -path "$LNX/arch/i386*" -prune -o               \
	-path "$LNX/include/asm-*" ! -path "$LNX/include/asm-i386*" -prune -o \
	-path "$LNX/tmp*" -prune -o                                           \
	-path "$LNX/Documentation*" -prune -o                                 \
	-path "$LNX/scripts*" -prune -o                                       \
	-path "$LNX/drivers*" -prune -o                                       \
        -name "*.[chxsS]" -print > $TARGET/cscope.files
    cd $TARGET
    cscope -bqk
}

if [ $# -eq 0 ]; then
	simple
else
	$1
fi
