#!/bin/bash

# this script compare two directory, and see what's the difference between
# the two.

function usage () {
	cat <<EOF

usage: $0 DIR1 DIR2

This script will compare the two directories provided, and show the
difference in two steps:

1. first, check whether they have the same file structure, if not, print
the difference and quit, or continue step 2.
2. second, calculate MD5SUM for each file, and list all the different
ones. 

EOF
	exit -2
}

function _log () {
	echo "### $1"
}

# check args
if [ $# -ne 2 ]; then
	usage
fi

# tools check
tools='md5 tree'
for tool in $tools; do
	if ! which $tool &> /dev/null ; then
		_log Please install tool \'$tool\' first.
		exit -1
	fi
done
MD5='md5 -q'

_log "[STEP1] Checking structure diff of dir '$1' and '$2'..."

# generate tree and check
tree_file_pre=/tmp/dir_tree
tree_file_1=${tree_file_pre}.1
tree_file_2=${tree_file_pre}.2
(cd $1; tree > $tree_file_1)
(cd $2; tree > $tree_file_2)
diff $tree_file_1 $tree_file_2
if [ $? -ne 0 ]; then
	_log "[FINAL] Detected structure diff, stop."
fi

_log "[STEP2] Looking for different files using MD5SUM..."

export same=1
(cd $1; find .) | while read f; do
	file1=$1/$f
	file2=$2/$f
	if [ ! -f $file1 -o ! -f $file2 ]; then
		continue;
	fi
	sum1=`$MD5 $file1`
	sum2=`$MD5 $file2`
	if [ "$sum1" != "$sum2" ]; then
		if [ $same != 0 ]; then
			same=0
			_log "Found differnet files:"
		fi
		_log " |- $f"
	fi
done

_log "[FINAL] ALL DONE. "
