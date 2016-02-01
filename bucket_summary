#!/usr/bin/env python

# parse data in bucket format, like:
# 100,3
# 120,5
# 140,1
# output max/min/aver value.

import os
import sys
import json

prog_name = sys.argv[0]
usage_msg = """
usage: %s <bucket_file>

Parse bucket data and generate a summary. Each line should follow:

A,B

A is data point, B is count of data point.
""" % prog_name

def err (s):
    print("ERROR: " + s)
    sys.exit(1)

def usage ():
    print(usage_msg)
    sys.exit(1)

args = sys.argv
if len(args) != 2:
    usage()
file_name = sys.argv[1]
if not os.access(file_name, os.R_OK):
    err("cannot read file '%s'" % file_name)
fd = open(file_name)

line_no = 0
d_min = -1
d_max = -1
d_total = 0
d_count = 0
data_list = []

while True:
    line = fd.readline()
    if not line:
        break
    line_no += 1
    line = line.strip()
    if not line:
        # empty line
        continue
    dataset = filter(lambda x:x, line.split(','))
    if len(dataset) != 2:
        err("failed to parse line %s: %s" % (line_no, line))
    data, count = map(float, dataset)
    if (data < 0):
        err("data < 0 in line %s: %s" % (line_no, line))
    if (count < 0):
        err("count < 0 in line %s: %s" % (line_no, line))
    if (int(count) != count):
        err("count not integer in line %s: %s" % (line_no, line))
    if d_min == -1:
        # init
        d_min = d_max = data
    else:
        if data < d_min:
            d_min = data
        if data > d_max:
            d_max = data
    data_list.append([data, count])
    if len(data_list) >= 2 and data < data_list[-2][0]:
        err("histogram not sorted!")
    d_total += data * count
    d_count += count

# find 99% point
n_99p = int(d_count * 0.99)
v_99p = -1
cur = 0
for data, count in data_list:
    cur += count
    if cur >= n_99p:
        v_99p = data
        break

print("summary: min=%s, aver=%s, max=%s, count=%s, v_99p=%s" \
      % (d_min, d_total / d_count, d_max, d_count, v_99p))
