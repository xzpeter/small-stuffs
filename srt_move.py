#!/usr/bin/python

# this is a simple tool to shift movie SRT timestamp.

import re
import sys

def to_sec(str):
    arr = map(int, str.split(":"))
    return arr[0]*3600 + arr[1]*60 + arr[2]

def to_str(n):
    hour = n/3600
    n %= 3600
    min = n/60
    n %= 60
    sec = n
    res = "%2s:%2s:%2s" % (hour, min, sec)
    res = res.replace(" ", "0")
    return res

if len(sys.argv) != 3:
    print "need filename, shift"
    exit (1)

shift = int(sys.argv[2])

for line in open(sys.argv[1], "r"):
    line = line.strip()
    times = re.findall(r"\d\d:\d\d:\d\d", line)
    if times:
        for t in times:
            n = to_sec(t)
            n += shift
            str = to_str(n)
            line = line.replace(t, str)
    print line
    
