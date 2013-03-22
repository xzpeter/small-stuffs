#!/bin/bash

# we should support things like:
# $ e file.c:14
# this should edit file.c with line 14
prms=`echo $@ | sed 's/\([^ :]\+\):\([0-9]\+\)/+\2 \1/g'`

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
