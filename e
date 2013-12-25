#!/bin/bash

# we have to use sed working both on Mac OS and Linux.
if uname | grep -qiE 'darwin|freebsd'; then
	# this is MacOS
	sed_prm=-E
elif uname | grep -qi linux; then
	sed_prm=-r
else
	echo "Unknown system!"
	exit 1
fi

# we should support things like:
# $ e file.c:14
# this should edit file.c with line 14
prms=`echo $@ | sed $sed_prm 's/([^ :]+):([0-9]+)/+\2 \1/g'`

function emacs_running ()
{
	pgrep -x emacs >/dev/null
}

emacsclient -a emacs $prms  >/dev/null 2>&1 &
# there are possibly one chance to fail, that is $#==0. Let's start emacs
# if no emacs running. 
if ! emacs_running && [[ $# == 0 ]] ; then
	emacs &
fi
