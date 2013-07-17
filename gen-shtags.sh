#!/bin/bash
etags --regex="/[ \t]*([a-zA-Z0-9_-]+)\([ \t]*\)/\1/" $@
