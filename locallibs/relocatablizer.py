#!/usr/bin/python

import os
import subprocess
import sys


CHMOD = "/bin/chmod"
OTOOL = "/usr/bin/otool"
INSTALL_NAME_TOOL = "/usr/bin/install_name_tool"
FILETOOL = "/usr/bin/file"


def do(cmd):
    '''Prints and executes cmd'''
    print " ".join(cmd)
    subprocess.check_call(cmd)


def fix_modes(framework_dir):
    '''Make sure all files are set so owner can read/write and everyone else
       can only read'''
    cmd = [CHMOD, "-R", "u+rw,g+r,g-w,o+r,o-w", framework_dir]
    print "Ensuring correct modes for files in %s..." % framework_dir
    subprocess.check_call(cmd)


def framework_parent_dir(some_file):
    '''Return parent path to framework dir'''
    temp_path = some_file
    while len(temp_path) > 1:
        if temp_path.endswith(".framework"):
            return os.path.dirname(temp_path)
        temp_path = os.path.dirname(temp_path)
    return temp_path


def framework_name(some_file):
    '''Return framework name'''
    temp_path = some_file
    while len(temp_path) > 1:
        if temp_path.endswith(".framework"):
            return os.path.basename(temp_path)
        temp_path = os.path.dirname(temp_path)
    return ""


def framework_lib_name(some_file):
    '''Return framework lib name'''
    return os.path.splitext(framework_name(some_file))[0]


def relativize_install_name(some_file):
    '''Replaces original install name with an rpath; returns new
    install_name'''
    original_install_name = get_install_name(some_file)
    if original_install_name and not original_install_name.startswith("@"):
        framework_loc = framework_parent_dir(some_file)
        new_install_name = os.path.join(
            "@rpath", os.path.relpath(some_file, framework_loc))
        cmd = [INSTALL_NAME_TOOL, "-id", new_install_name, some_file]
        do(cmd)
        return new_install_name
    return original_install_name


def fix_dep(some_file, old_install_name, new_install_name):
    '''Updates old_install_name to new_install_name inside some file'''
    cmd = [INSTALL_NAME_TOOL,
           "-change", old_install_name, new_install_name, some_file]
    do(cmd)


def add_rpath(some_file):
    '''adds an rpath to the file'''
    framework_loc = framework_parent_dir(some_file)
    rpath = os.path.join(
        "@executable_path", 
        os.path.relpath(framework_loc, 
                        os.path.dirname(some_file))) + "/"
    cmd = [INSTALL_NAME_TOOL, "-add_rpath", rpath, some_file]
    do(cmd)


def get_deps(some_file):
    '''Return a list of dependencies for some_file'''
    cmd = [OTOOL, "-L", some_file]
    output_lines = subprocess.check_output(cmd).splitlines()
    deps = []
    if len(output_lines) > 1:
        for line in output_lines[1:]:
            line = line.lstrip()
            tail = line.find(" (compatibility")
            if tail != -1:
                line = line[0:tail]
            deps.append(line)
    return deps


def get_install_name(some_file):
    '''Returns the install_name of a shared library'''
    cmd = [OTOOL, "-D", some_file]
    output_lines = subprocess.check_output(cmd).splitlines()
    if len(output_lines) > 1:
        return output_lines[1]
    return ""


def make_info(some_file):
    '''Return a dict containing info about the file'''
    info = {}
    info["path"] = some_file
    install_name = get_install_name(some_file)
    if install_name:
        info["install_name"] = install_name
        info["dependencies"] = get_deps(some_file)[1:]
    else:
        info["dependencies"] = get_deps(some_file)
    return info


def deps_contain_prefix(info_item, prefix):
    '''Do the deps or install_name contain the prefix?'''
    matching_dep_items = len([dep_item 
                              for dep_item in info_item.get("dependencies", [])
                              if dep_item.startswith(prefix)]) > 0
    matching_install_name = info_item.get("install_name", "").startswith(prefix)
    return matching_dep_items or matching_install_name


def base_install_name(full_framework_path):
    versions_dir = os.path.join(full_framework_path, "Versions")
    versions = [os.path.join(versions_dir, item)
                for item in os.listdir(versions_dir)
                if os.path.isdir(os.path.join(versions_dir, item))
                and not os.path.islink(os.path.join(versions_dir, item))]
    for version_dir in versions:
        dylib_name = os.path.join(version_dir, "Python")
        if os.path.exists(dylib_name):
            install_name = get_install_name(dylib_name)
            if not install_name.startswith("@"):
                parent_dir = framework_parent_dir(install_name)
                name = framework_name(install_name)
                return os.path.join(parent_dir, name)
    return ""


def analyze(some_dir):
    """Finds files we need to tweak"""
    print "Analyzing %s..." % some_dir
    prefix = base_install_name(some_dir)
    #if prefix == "":
    #    print "Can't determine base install_name"
    #    exit()
    data = {}
    data["executables"] = []
    data["dylibs"] = []
    data["so_files"] = []
    count = 0
    for dirpath, dirs, files in os.walk(some_dir):
        for some_file in files:
            count += 1
            if count % 100 == 0:
                sys.stdout.write(".")
                sys.stdout.flush()
            filepath = os.path.join(dirpath, some_file)
            if not os.path.islink(filepath):
                name, ext = os.path.splitext(filepath)
                if ext == ".so":
                    info = make_info(filepath)
                    if deps_contain_prefix(info, prefix):
                        data["so_files"].append(info)
                elif ext == ".dylib":
                    info = make_info(filepath)
                    if deps_contain_prefix(info, prefix):
                        data["dylibs"].append(info)
                else:
                    cmd = [FILETOOL, "-b", filepath]
                    output = subprocess.check_output(cmd)
                    if "Mach-O 64-bit executable" in output:
                        info = make_info(filepath)
                        if deps_contain_prefix(info, prefix):
                            data["executables"].append(info)
                    if "Mach-O 64-bit dynamically linked shared library" in output:
                        info = make_info(filepath)
                        if deps_contain_prefix(info, prefix):
                            data["dylibs"].append(info)
    sys.stdout.write("\n")
    return data


def relocatablize(framework_path):
    '''Changes install names and rpaths inside a (Python) framework to make
    it relocatable. Might work with non-Python frameworks...'''
    full_framework_path = os.path.abspath(
        os.path.normpath(os.path.expanduser(framework_path)))
    fix_modes(full_framework_path)
    framework_data = analyze(full_framework_path)
    for dylib in framework_data["dylibs"]:
        old_install_name = dylib["install_name"]
        new_install_name = relativize_install_name(dylib["path"])
        # update other files with new install_name
        if old_install_name != new_install_name:
            files = (framework_data["executables"] + framework_data["dylibs"] +
                     framework_data["so_files"])
            for item in files:
                if old_install_name in item["dependencies"]:
                    fix_dep(item["path"], old_install_name, new_install_name)
        print
    # add rpaths to executables
    for item in framework_data["executables"]:
        add_rpath(item["path"])
