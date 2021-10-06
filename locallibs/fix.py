# encoding: utf-8
#
# Copyright 2018 Greg Neagle.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Functions to fix other things about the Python framework"""

from __future__ import print_function

import os
import shutil
import subprocess
import sys


def ensure_current_version_link(framework_path, short_version):
    '''Make sure the framework has Versions/Current'''
    versions_current_path = os.path.join(framework_path, "Versions/Current")
    if not os.path.exists(versions_current_path):
        specific_version = os.path.join(
            framework_path, "Versions", short_version)
        if not os.path.exists(specific_version):
            print("Path %s doesn't exist!" % short_version, file=sys.stderr)
            return False
        try:
            print("Creating Versions/Current symlink...")
            os.symlink(short_version, versions_current_path)
        except OSError as err:
            print("Could not create Versions/Current symlink to %s: %s"
                  % (short_version, err), file=sys.stderr)
            return False
    return True


def relativize_interpreter_path(framework_path, script_dir, shebang_line):
    '''Takes a shebang line and generates a relative path to the interpreter
    from the script dir. This is complicated by the fact the shebang line
    might start with the current framework_path _or_
    the default framework path'''
    original_path = shebang_line[2:]
    current_framework_path = os.path.abspath(framework_path).encode("UTF-8")
    default_framework_path = b"/Library/Frameworks/Python.framework"
    # normalize the original path so it refers to the current framework path
    if original_path.startswith(default_framework_path):
        original_path = original_path.replace(
            default_framework_path, current_framework_path, 1)
    return os.path.relpath(
        original_path, os.path.abspath(script_dir).encode("UTF-8"))


def is_framework_shebang(framework_path, text):
    """Returns a boolean to indicate if the text starts with a shebang
    referencing the framework_path or the default
    /Library/Frameworks/Python.framework path"""
    this_framework_shebang = b"#!" + os.path.abspath(framework_path).encode("UTF-8")
    prefixes = [
        this_framework_shebang,
        b"#!/Library/Frameworks/Python.framework",
        b"#!/Library/Developer/CommandLineTools/usr/bin/python3",
        b"#!/Applications/Xcode.app/Contents/Developer/usr/bin/python3",
    ]
    return any(text.startswith(x) for x in prefixes)


def fix_script_shebangs(framework_path, short_version):
    '''Attempt to make the scripts in the bin directory relocatable'''

    relocatable_shebang = b"""#!/bin/sh
'''exec' "$(dirname "$0")/%s" "$0" "$@"
' '''
# the above calls the %s interpreter relative to the directory of this script
"""
    bin_dir = os.path.join(framework_path, "Versions", short_version, "bin")
    for filename in os.listdir(bin_dir):
        try:
            original_filepath = os.path.join(bin_dir, filename)
            if (os.path.islink(original_filepath) or
                    os.path.isdir(original_filepath)):
                # skip symlinks and directories
                continue
            with open(original_filepath, 'rb') as original_file:
                first_line = original_file.readline().strip()
                if is_framework_shebang(framework_path, first_line):
                    # we found a script that references an interpreter inside
                    # the framework
                    print("Modifying shebang for %s..." % original_filepath)
                    relative_interpreter_path = relativize_interpreter_path(
                        framework_path, bin_dir, first_line)
                    new_filepath = original_filepath + ".temp"
                    with open(new_filepath, 'wb') as new_file:
                        new_file.write(
                            relocatable_shebang
                            % (relative_interpreter_path,
                               relative_interpreter_path)
                        )
                        for line in original_file.readlines():
                            new_file.write(line)
                    # replace original with modified
                    shutil.copymode(original_filepath, new_filepath)
                    os.remove(original_filepath)
                    os.rename(new_filepath, original_filepath)
        except (IOError, OSError) as err:
            print("Could not fix shebang for %s: %s"
                  % (os.path.join(bin_dir, filename), err))
            return False
    return True


def fix_other_things(framework_path, short_version):
    '''Wrapper function in case there are other things we need to fix in the
    future'''
    return (ensure_current_version_link(framework_path, short_version) and
            fix_script_shebangs(framework_path, short_version))


def fix_broken_signatures(files_relocatablized):
    """
    Re-sign the binaries and libraries that were relocatablized with ad-hoc
    signatures to avoid them having invalid signatures and to allow them to
    run on Apple Silicon
    """
    CODESIGN_CMD = ["/usr/bin/codesign",
                    "-s", "-", "--deep", "--force",
                    "--preserve-metadata=identifier,entitlements,flags,runtime"]
    for pathname in files_relocatablized:
        print("Re-signing %s with ad-hoc signature..."
              % pathname)
        cmd = CODESIGN_CMD + [pathname]
        subprocess.check_call(cmd)
