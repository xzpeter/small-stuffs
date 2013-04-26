#!/bin/bash

# generate and update cscope files

function simple {
	find $PWD -name "*.c" -o -name "*.h" -o -name "*.cpp" \
		-o -name "*.cxx" -o -name "*.hxx" > cscope.files
	cscope -bqk
}

function kernel {
	find $PWD -not -path "$PWD/arch/*" -a -name "*.[chxsS]" > cscope.files
	find $PWD -path "$PWD/arch/x86/*" -a -name "*.[chxsS]" >> cscope.files
	cscope -bqk
}

if [ $# -eq 0 ]; then
	simple
else
	echo "indexing kernel...."
	kernel
fi
