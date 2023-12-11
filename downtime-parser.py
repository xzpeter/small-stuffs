#!/usr/bin/env python3

import json
import sys
import re

# How many non-iterable entries to dump
SHOW_TOP_N = 10

def usage():
    print("")
    print("usage: %s <file>\n" % sys.argv[0])
    print("Analyze downtime captured by QEMU tracepoints (vmstate_downtime_*).")
    print("It can be either captured on src or dst.")
    print("")
    exit(0)

if len(sys.argv) < 2:
    usage()

def parse_log(logfile):
    checkpoints = []
    devices = {"iterable": [], "non-iterable": []}

    log = open(logfile)
    while True:
        line = log.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            # empty line
            continue
        out = re.match('^[0-9]+@([0-9]+) vmstate_downtime_([a-z]*) (.*)$', line)
        if not out:
            continue
        time_ns, trace_type, params = out.groups()
        if trace_type == "checkpoint":
            checkpoints.append([int(time_ns), params])
        elif trace_type in ["save", "load"]:
            out = re.match("^type=(.*) idstr=(.*) instance_id=(.*) downtime=([0-9]+)$", params)
            vmsd_type, dev_id, ins_id, downtime = out.groups()
            if vmsd_type not in devices.keys():
                raise Exception("VMSD type '%s' unknown" % vmsd_type)
            devices[vmsd_type].append([trace_type, dev_id, int(ins_id), int(downtime)])
        else:
            raise Exception("Unrecognized line (type=%s): '%s'" % (trace_type, line))
    log.close()

    return [checkpoints, devices]

def dump_checkpoints(checkpoints):
    prev_ts = prev_stage = None
    print("Checkpoints analysis:\n")
    for cp in checkpoints:
        ts, stage = cp
        # convert nanoseconds to microseconds
        ts = int(ts / 1000)
        if prev_stage:
            print("  %24s -> %24s: %20s (us)" % (prev_stage, stage, ts - prev_ts))
        prev_ts = ts
        prev_stage = stage
    print("")

def dump_one_device(dev):
    trace_type, dev_id, ins_id, downtime = dev
    print("  Device %s of %40s:%03s took %10s (us)" % (trace_type.upper(), dev_id, ins_id, downtime))

def dump_devices(devices):
    global SHOW_TOP_N

    for entry in devices.keys():
        # Sort with downtime
        devices[entry].sort(key=lambda x: x[3], reverse=True)

    print("Iterable device analysis:\n")
    for dev in devices["iterable"]:
        dump_one_device(dev)
    print("")

    print("Non-iterable device analysis:\n")
    count = 0
    for dev in devices["non-iterable"]:
        if count == SHOW_TOP_N:
            print("  (%d vmsd omitted)" % (len(devices["non-iterable"]) - count))
            break
        dump_one_device(dev)
        count += 1
    print("")

checkpoints, devices = parse_log(sys.argv[1])

dump_checkpoints(checkpoints)
dump_devices(devices)
