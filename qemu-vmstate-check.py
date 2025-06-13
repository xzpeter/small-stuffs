#!/usr/bin/env python3

import subprocess
import argparse
import shutil
import json
import sys
import os

SCRIPT = sys.argv[0]
ARCHS_DEFAULT = "x86_64,s390x,aarch64,ppc64"
QEMU_ROOT = os.getcwd()
VMSTATE_CHECKER = os.path.join(QEMU_ROOT, "scripts", "vmstate-static-checker.py")

# Directories layout:
#
# vmstate-check/
#   build-curerent/                      Build for current git commit
#   build-previous/                      Build for previous release
#   results/                             Keep all the results
WORK_DIR = os.path.join(QEMU_ROOT, "vmstate-check")
BUILD_DIR_CUR = os.path.join(WORK_DIR, "build-current")
BUILD_DIR_PREV = os.path.join(WORK_DIR, "build-previous")
RESULTS_DIR = os.path.join(WORK_DIR, "results")

def run_cmd(cmd, cwd=None):
    print(f"Running: {' '.join(cmd)} (CWD={cwd if cwd else os.getcwd()})")
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, err = proc.communicate()
    return proc.returncode, out, err

def run(cmd, cwd=None):
    ret, out, err = run_cmd(cmd, cwd)
    if ret != 0:
        raise Exception(f"Command {cmd} failed.\nSTDOUT:\n{out}\nSTDERR:\n{err}\n")
    return out

def get_version_from_file():
    with open(os.path.join(QEMU_ROOT, "VERSION")) as f:
        version = f.read().strip()
    major, minor = version.split(".")[:2]
    return f"v{major}.{minor}.0"

def configure_and_build(build_dir, archs):
    os.makedirs(build_dir, exist_ok=True)
    config_cmd = [
        os.path.join(QEMU_ROOT, "configure"),
        "--disable-docs",
        "--target-list=" + ",".join(map(lambda x: f"{x}-softmmu", archs))
    ]
    run(config_cmd, cwd=build_dir)
    run(["make", f"-j{os.cpu_count()}"], cwd=build_dir)

def get_supported_machine_types(qemu_binary):
    result = run([qemu_binary, "-machine", "help"])
    machines = []
    for line in result.splitlines():
        if line.startswith("Supported machines"):
            continue
        if line.find("deprecated") > 0:
            continue
        if line.find("alias of") > 0:
            continue
        mach = line[:line.find(" ")]
        machines.append(mach)
    return machines

def dump_vmstate(binary, machine, output_file):
    run([binary, "-machine", machine, "-dump-vmstate", output_file])

def compare_dump(dump1, dump2):
    # STDERR isn't used
    ret, out, err = run_cmd([VMSTATE_CHECKER, "-s", dump1, "-d", dump2])
    if not ret:
        return []
    return list(filter(lambda x: x, out.split("\n")))

def compare_dumps(prev, cur, output_file):
    # Forward and backward migrations
    forward = compare_dump(prev, cur)
    backward = compare_dump(cur, prev)
    final = {
        "forward": forward,
        "backward": backward,
    }
    with open(output_file, "w") as f:
        f.write(json.dumps(final, indent=4))

def build_binaries(archs):
    # Build current
    configure_and_build(BUILD_DIR_CUR, archs)
    # Build previous released version
    run(["git", "checkout", get_version_from_file()])
    configure_and_build(BUILD_DIR_PREV, archs)

def check_arch(arch):
    # For each arch, dump machine types and compare
    os.makedirs(RESULTS_DIR, exist_ok=True)

    arch_dir = os.path.join(RESULTS_DIR, arch)
    os.makedirs(arch_dir, exist_ok=True)

    bin_name = f"qemu-system-{arch}"
    bin_cur = os.path.join(BUILD_DIR_CUR, bin_name)
    bin_prev = os.path.join(BUILD_DIR_PREV, bin_name)

    if not os.path.exists(bin_cur):
        raise Exception(f"Binary {bin_cur} missing!")
    if not os.path.exists(bin_prev):
        raise Exception(f"Binary {bin_prev} missing!")

    dump_dir_cur = os.path.join(BUILD_DIR_CUR, arch)
    os.makedirs(dump_dir_cur, exist_ok=True)
    dump_dir_prev = os.path.join(BUILD_DIR_PREV, arch)
    os.makedirs(dump_dir_prev, exist_ok=True)
    result_dir = os.path.join(RESULTS_DIR, arch)
    os.makedirs(result_dir, exist_ok=True)

    cur_machines = set(get_supported_machine_types(bin_cur))
    prev_machines = set(get_supported_machine_types(bin_prev))
    common_machines = cur_machines & prev_machines

    for machine in sorted(common_machines):
        dump_cur = os.path.join(dump_dir_cur, f"{machine}.json")
        dump_prev = os.path.join(dump_dir_prev, f"{machine}.json")
        dump_vmstate(bin_cur, machine, dump_cur)
        dump_vmstate(bin_prev, machine, dump_prev)
        result_file = os.path.join(result_dir, f"{machine}.json")
        compare_dumps(dump_prev, dump_cur, result_file)

def generate_vmstate_results(archs):
    print("Start generating vmstate compatibility check reports...")
    original_commit = run(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()
    try:
        build_binaries(archs)
        for arch in archs:
            check_arch(arch)
    finally:
        run(["git", "checkout", original_commit])

# Sample:
#
# {
#     "forward": [],
#     "backward": [
#         "Section \"isa-ipmi-bt\" does not exist in dest",
#         "Section \"ipmi-bmc-extern\" does not exist in dest",
#         "Section \"isa-ipmi-kcs\" does not exist in dest",
#         "Section \"ipmi-bmc-sim\" does not exist in dest",
#     ]
# }
def parse_one(path):
    return json.loads(open(path).read())
    
def parse_vmstate_results(archs):
    results = {}
    for key in ["forward", "backward"]:
        results[key] = {}
    for arch in archs:
        arch_dir = os.path.join(RESULTS_DIR, arch)
        for f in os.listdir(arch_dir):
            mach = f.split(".")[0]
            one = parse_one(os.path.join(arch_dir, f))
            for key in results.keys():
                # If there's an incompatibility detected either key..
                if one[key]:
                    errors = one[key]
                    for err in errors:
                        # If it's the first occurance, push the error
                        if err not in results[key]:
                            results[key][err] = []
                        results[key][err].append((arch, mach))
    print("")
    for key in results:
        if not results[key]:
            print(f"No {key} migration incompatibility found!\n")
        else:
            print(f"Found {key} migration incompatibility issues:\n")
            for err in results[key]:
                print(f"  {err}\n")
                systems = results[key][err]
                print(f"  (occurs in {len(systems)} systems: {json.dumps(systems)}")
                print("")

def cleanup_vmstate_results():
    shutil.rmtree(WORK_DIR)

def main():
    help_text = f"""
This tool should only be run under QEMU's root git repository.

It leverages vmstate-static-checker.py script to detect any possible
vmstate incompatibility on the current git commit, against the most recent
released QEMU version.

It will automatically build the binaries needed.  All the results
(build outputs, parse results) will be put under:

    {WORK_DIR}

To use this script, one should first generate the results using:

    $ {SCRIPT} -g

This will generate the vmstate check results.  Then parse it using:

    $ {SCRIPT} -p

To provide a summary of the previous check. To clean all the generated
files after that, one can use:

    $ {SCRIPT} -c
"""
    parser = argparse.ArgumentParser(
        description=help_text, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-a', '--arch', type=str, default=ARCHS_DEFAULT,
                        help=f'List of archs to check (default: {ARCHS_DEFAULT})')
    parser.add_argument('-c', '--cleanup', action='store_true',
                        help=f'Clean up the previous results generated')
    parser.add_argument('-g', '--generate', action='store_true',
                        help=f'Parse the results generated')
    parser.add_argument('-p', '--parse', action='store_true',
                        help=f'Parse the results generated')
    args = parser.parse_args()
    archs = args.arch.split(",")

    if args.generate:
        generate_vmstate_results(archs)
    elif args.parse:
        parse_vmstate_results(archs)
    elif args.cleanup:
        cleanup_vmstate_results()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
