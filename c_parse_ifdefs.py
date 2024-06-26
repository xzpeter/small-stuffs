#!/usr/bin/env python3
#
# This script is used to parse a partial C source code and dump the nested
# "ifdef" blocks, so that if you're going to insert new codes under the
# cursor you'll know when it will be compiled at all.
#
# You'll normally need to feed stdin with the buffer of (0, current_line)
# of your C source file, and then it'll spit the ifdef stack out.  I assume
# you use this with some scripting like Emacs Lisp otherwise it's awkward
# to be used manually somehow.  An Emacs Lisp function can look like:
#
# (defun my-c-parse-ifdefs ()
#  (interactive)
#  (shell-command-on-region (point-min) (point) "c_parse_ifdefs.py"))
#

import json
import sys
import re

line_no = 0

pat_if = re.compile(r'^\s*#\s*(ifdef|ifndef|if\s+)')
pat_elif = re.compile(r'^\s*#\s*elif')
pat_else = re.compile(r'^\s*#\s*else')
pat_end = re.compile(r'^\s*#\s*endif')
pat_cont = re.compile(r'.*\\\s*$')

def error():
    global line_no
    print("Error at line %d" % line_no)
    sys.exit(-1)

def stack_check_non_empty(stack):
    if not stack:
        print("Empty stack found where it shouldn't!")
        error()

def stack_check_last(stack, target):
    if isinstance(target, str):
        target = [target]
    stack_check_non_empty(stack)
    last = stack[-1][0]
    if last not in target:
        print("Found entry '%s', expecting '%s'!" % (last, target))
        print("Dumping wrong stack:")
        print(json.dumps(stack, indent=4))
        error()

def c_ifdefs_parse(lines):
    global line_no
    stack = []
    line_no = 0
    need_append = False
    for line in lines:
        line_no += 1
        matched = True
        if need_append:
            stack_check_non_empty(stack)
            stack[-1][1] += line
            need_append = False
        elif pat_if.match(line):
            stack.append(["if", line])
        elif pat_elif.match(line):
            stack_check_last(stack, ["if", "elif"])
            stack.append(["elif", line])
        elif pat_else.match(line):
            stack_check_last(stack, ["if", "elif"])
            stack.append(["else", line])
        elif pat_end.match(line):
            stack_check_non_empty(stack)
            while True:
                last = stack[-1][0]
                if last in ["if", "elif", "else"]:
                    stack.pop()
                if last == "if":
                    break
        else:
            matched = False

        # Check continuous lines, append them to previous
        if matched and pat_cont.match(line):
            need_append = True

    return stack

def c_ifdefs_print(stack):
    if not stack:
        print("[EMPTY IFDEF STACK]")
        return
    print("[IFDEF STACK DUMP]")
    print("")
    for entry in stack:
        print(entry[1].strip())

stack = c_ifdefs_parse(sys.stdin)
c_ifdefs_print(stack)
