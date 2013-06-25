#!/bin/bash
# generate sh tags
etags --regex-sh='/^\s+(\S+)\(/\1/' --language-force=sh $@
