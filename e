#!/bin/bash

emacsclient -a emacs $@  >/dev/null 2>&1 &
# there are possibly one chance to fail, that is $#==0. Let's start emacs
# if no emacs running. 
if ! pgrep -f emacs &>/dev/null && [[ $# == 0 ]] ; then
	emacs &
fi
