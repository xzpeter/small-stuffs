#!/bin/bash

function emacs_running ()
{
	ps aux | grep -v grep | grep -q emacs
}

emacsclient -a emacs23 $@  >/dev/null 2>&1 &
# there are possibly one chance to fail, that is $#==0. Let's start emacs
# if no emacs running. 
if ! emacs_running && [[ $# == 0 ]] ; then
	emacs &
fi
