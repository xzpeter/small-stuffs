#!/usr/bin/env python

# this tool is used to parse kickstart configuration & comps.xml file in
# centos iso image, to list all dependent package names. This should be useful
# when you are trying to build customized centos ISO images using kickstart.

import os
import sys
import json
import xmltodict

prog_name = sys.argv[0]

def usage():
        print("usage: %s <xmlfile> <kickstart_config>" % prog_name)
        sys.exit(1)

def err(s):
        raise Exception("ERROR: " + s)

def parse_groups(xml_file):
        for item in [xml_file, ks_config]:
                if not os.access(item, os.R_OK):
                        err("File %s not readable" % name)
        xml_data = open(xml_file).read()
        info_dict = xmltodict.parse(xml_data)
        groups = info_dict["comps"]["group"]
        # print(json.dumps(groups, indent=4))
        return groups

def parse_ks_config(ks_config):
        """Parse ks.cfg into a list of required packages"""
        fh = open(ks_config)
        start_flag = 0
        pkg_list = []
        while True:
                line = fh.readline().strip()
                if not line:
                        continue
                if line[0] == "#":
                        continue
                if line == "%packages":
                        start_flag = 1
                        continue
                if start_flag:
                        # during the "%packages" thing...
                        if line == "%end":
                                # we are done
                                break
                        pkg_list.append(line)
        # print(json.dumps(pkg_list, indent=4))
        return pkg_list

def expand_groups(origin, groups):
        pkg_hash = {}
        def find_group(group, groups):
                for item in groups:
                        if item["id"] == group:
                                return item
                return None
        def expand_item_and_insert(item, groups, pkg_hash):
                if item[0] != "@":
                        # this is a standalone pkg
                        if item not in pkg_hash:
                                pkg_hash[item] = 1
                        else:
                                pkg_hash[item] += 1
                        return
                # then... this is a group of pkgs
                group = find_group(item[1:], groups)
                if not group:
                        err("Failed to find group: %s" % item)
                pkg_list = group["packagelist"]["packagereq"]
                for pkg in pkg_list:
                        pkg_name = pkg["#text"]
                        expand_item_and_insert(pkg_name, groups, pkg_hash)

        for item in origin:
                # expand the item (group or standalone pkg) and insert all the
                # parsed out pkg list into pkg_hash
                expand_item_and_insert(item, groups, pkg_hash)

        # print(json.dumps(pkg_hash, indent=4))
        return pkg_hash.keys()

if len(sys.argv) != 3:
        usage()

xml_file = sys.argv[1]
ks_config = sys.argv[2]

groups_info = parse_groups(xml_file)
required_pkgs_origin = parse_ks_config(ks_config)
required_pkgs_list = expand_groups(required_pkgs_origin, groups_info)
for pkg in required_pkgs_list:
        print(pkg)
