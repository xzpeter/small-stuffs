#!/usr/bin/env python3

import sys
import json
import re

example="""
4d5f26ee3102 kvm: selftests: fix spelling mistake: "divisable" and "divisible"
6089ae0bd5e1 kvm: selftests: add sync_regs_test
783e9e51266e kvm: selftests: add API testing infrastructure
"""

def help():
    print("")
    print("usage: %s <upstream_commits> <downstream_commits>" % sys.argv[0])
    print("")
    print("Will output what commits are missing for downstream.")
    print("")
    print("Example commit list file:\n%s" % example)
    sys.exit(0)

def parse_msg(msg):
    # Remove downstream tags if there are any
    msg = re.sub("^\[.*\] *", "", msg)
    return msg

def parse_commits(file):
    data = open(file).read().split("\n")
    output = []
    for line in data:
        line = line.strip()
        if not line:
            continue
        tmp = line.split(" ", 1)
        if re.search("^Merge tag ", tmp[1]):
            # Skip upstream merge commits
            continue
        entry = {}
        entry["id"] = tmp[0]
        entry["msg"] = parse_msg(tmp[1])
        output.append(entry)
    return output

if len(sys.argv) < 3:
    help()

up=sys.argv[1]
down=sys.argv[2]

up_commits = parse_commits(up)
down_commits = parse_commits(down)
# Sometimes downstream uses lower case for commit subject... Let's
# filter these...
down_list = list(map(lambda x: x["msg"].lower(), down_commits))
port_list = []

for entry in up_commits:
    msg = entry["msg"]
    lower = entry["msg"].lower()
    if lower in down_list:
        down_list.remove(lower)
        #print("Commit '%s' in downstream, skip" % entry["msg"])
    else:
        port_list.append(entry)
        #print("Commit '%s' missing" % entry["msg"])

# list from old to new
port_list.reverse()

print("\nPlease backport these commits to rebase to upstream:\n")
for entry in port_list:
    print("%s %s" % (entry["id"], entry["msg"]))

if down_list:
    print("\nPLEASE CHECK: DOWNSTREAM-ONLY PATCHES (LOWER-CASED):\n")
    for entry in down_list:
        print("  %s" % entry)
    
