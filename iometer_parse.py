#!/usr/bin/python
import os
import sys
import json
import re
import copy

def err (msg):
        print msg
        exit (1)

if len(sys.argv) == 1:
        err("Please specify iometer result file name")

file_name = sys.argv[1]

if not os.access(file_name, os.R_OK):
        err("File %s not accessible" % file_name)

data = open(file_name).read().split("\n")
# only collect over-all data
data = filter(lambda line: line[0:3] == "ALL", data)
results = {}

def guess_io_size (name):
        res = re.search(r"\d+[kmKM]?[bB]?", name)
        if not res:
                err("Failed parse io size: " + name)
        io_size = res.group().upper()
        if io_size[-1] not in "bB":
                io_size += "B"
        return io_size

def iosize_int (size):
        _table = {
                "K": 1024,
                "M": 1024*1024,
        }
        _size = size
        if "B" == _size[-1]:
                _size = _size[:-1]
        if _size[-1].isdigit():
                _unit = 1
                _num = int(_size)
        else:
                _unit = _table[_size[-1]]
                _num = int(_size[:-1]) * _unit
        return _num

def iosize_cmp (x, y):
        _x = iosize_int(x)
        _y = iosize_int(y)
        if _x == _y:
                return 0
        elif _x > _y:
                return 1
        else:
                return -1

for line in data:
        _list = line.split(",")
        _name = _list[2]
        _iosize = guess_io_size(_name)
        _results = {
                "name": _name,
                "io_size": _iosize,
                "data": {
                        "read": {
                                "iops": float(_list[7]),
                                "bw": float(_list[10])
                        },
                        "write": {
                                "iops": float(_list[8]),
                                "bw": float(_list[11])
                        }
                }
        }
        results[_results["name"]] = _results

diagram = {}

# fill in IO type (R/W)
for result in results.values():
        if result["data"]["read"]["iops"] != 0 and \
           result["data"]["write"]["iops"] == 0:
                _type = "read"
        elif result["data"]["read"]["iops"] == 0 and \
             result["data"]["write"]["iops"] != 0:
                _type = "write"
        else:
                err ("unknown rw type")
        result["type"] = _type
        _iosize = result["io_size"]
        if _iosize not in diagram:
                diagram[_iosize] = {}
        diagram[_iosize][_type] = result["data"][_type]

line_format = "%16s%16s%16s%16s%16s"
print line_format % ("IOSIZE", "ReadIOPS", "ReadBW", "WriteIOPS", "WriteBW")

def float_str (f):
        return "%.2f" % f

size_list = copy.deepcopy(diagram.keys())
size_list.sort(cmp=iosize_cmp)
for data in size_list:
        value = diagram[data]
        print line_format % (
                data,
                float_str(value["read"]["iops"]),
                float_str(value["read"]["bw"]),
                float_str(value["write"]["iops"]),
                float_str(value["write"]["bw"])
        )
