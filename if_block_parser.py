#!/usr/bin/python

# this is a script that helps find "#if 0" blocks in a C program.

import sys

PROG_NAME = sys.argv[0]
macro_name = "0"

USAGE = """
usage: %s <cmd> <c_source> [MACRO]

This tool helps parse "#if MACRO" blocks in C source code.

Supported cmds:

dump            will only dump "#if MACRO" blocks one by one.
remove          will remove all "#if MACRO" blocks in file.
check_bracket   will dump blocks that has asymmetric brackets
                (this check is useful for you to diagnose cscope
                 fail parsing issue)

MACRO is optional parameter. If not specified, the default MACRO
is "%s".
""" % (PROG_NAME, macro_name)

def usage():
        print USAGE
        sys.exit(0)

class basic_cmd:
        def start_block (self, stack, line):
                pass
        def each_line (self, stack, line):
                pass
        def end_block (self, block, line):
                pass

class dump_cmd (basic_cmd):
        def end_block (self, block, line):
                print "DUMP BLOCK:"
                print block["data"]

class remove_cmd (basic_cmd):
        def each_line (self, stack, line):
                if not stack:
                        # not in any block
                        print line

class check_bracket_cmd (basic_cmd):
        def end_block (self, block, line):
                # check whether all brackets are symmetric in current block
                bracket_pairs = {
                        "{": "}",
                        "(": ")",
                        "[": "]",
                }
                bracket_stack = []
                mismatch = False
                for char in block["data"]:
                        if char in bracket_pairs.keys():
                                # this is a left
                                bracket_stack.append(char)
                        elif char in bracket_pairs.values():
                                # this is a right
                                if not bracket_stack:
                                        # no left?
                                        mismatch = True
                                        break
                                prev = bracket_stack.pop()
                                target = bracket_pairs[prev]
                                if target != char:
                                        mismatch = True
                                        break
                # if mismatch is set, or we have extra brackets, then there are
                # mismatching pairs.
                if mismatch or bracket_stack:
                        print "MISMATCH BLOCK FOUND:"
                        print block["data"]

args = sys.argv
if len(args) < 3 or len(args) > 4:
        usage()

cmd = args[1]
if cmd == "dump":
        cmd = dump_cmd()
elif cmd == "remove":
        cmd = remove_cmd()
elif cmd == "check_bracket":
        cmd = check_bracket_cmd()
else:
        print "command %s not known." % cmd
        usage()
file_name = args[2]
if len(args) == 4:
        macro_name = args[3]

header_line = "#if %s" % macro_name
content = open(file_name).read()
stack = []
for line in content.split("\n") :
        if line.startswith("#if"):
                # this is start of a block (could nest)
                stack.append({"start": line,
                              # this is used to store data in block
                              "data": ""})
                if line.startswith(header_line):
                        # trigger "start block" fn
                        cmd.start_block(stack, line)

        # insert data into block if there is any
        for frame in stack:
                newline = line + "\n"
                frame["data"] += newline
        # trigger cmd hook function
        cmd.each_line(stack, line)

        if line.startswith("#endif"):
                # close one block
                block = stack.pop()
                if block["start"].startswith(header_line):
                        # trigger "end block" fn
                        cmd.end_block(block, line)
