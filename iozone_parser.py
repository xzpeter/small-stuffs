#!/usr/bin/python

# Parse iozone result

# will parse all files under this directory

import os
import json

# file larger than 10k is omitted
MAX_FILE_SIZE = 10000

def err (s):
        print s
        exit (1)

def parse_one_result (fname):
        lines = open(fname).read().split("\n")
        result = {}
        for line in lines:
                if "Record Size" in line:
                        record_size = line.replace(
                                "Record Size", "").strip()
                        record_size = int(record_size.replace(
                                " ", "").replace("kB", ""))
                        unit = "KB"
                        result["record_size_kb"] = record_size
                        if record_size >= 1024:
                                record_size >>= 10
                                unit = "MB"
                        result["record_size_str"] = "%s%s" % (record_size, unit)
                elif "Children see throughput" in line:
                        bw = float(line.split("=", 1)[1].strip().\
                                   split(" ", 1)[0]) / 1000
                        if "write" in line:
                                result["seq_write"] = bw
                        elif "read" in line:
                                result["seq_read"] = bw
                        else:
                                err("Unknown line: " + line)
        for key in ["record_size_kb",
                    "seq_read",
                    "seq_write"]:
                if key not in result:
                        err("Key '%s' missing" % key)
        return result

def parse_all_results (dirname):
        files = os.listdir(dirname)
        results = []
        for fname in files:
                fsize = os.stat(fname).st_size
                # file too large is omitted
                if fsize >= MAX_FILE_SIZE:
                        print "File '%s' size too big, skip" \
                                % fname
                        continue
                result = parse_one_result(fname)
                results.append(result)
        results.sort(key=lambda x: x["record_size_kb"])
        return results

def print_results (results):
        # result should be sorted
        print "%12s%12s%12s" % ("Block Size", "Seq Read", "Seq Write")
        for result in results:
                print "%12s%12.2f%12.2f" % \
                        (result["record_size_str"],
                         result["seq_read"],
                         result["seq_write"])

def main ():
        results = parse_all_results(".")
        print_results(results)

main()
