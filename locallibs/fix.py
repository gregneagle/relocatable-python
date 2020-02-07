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


def fix_script_shebangs(framework_path, short_version):
    '''Attempt to make the scripts in the bin directory relocatable'''

    relocatable_shebang = b"""#!/bin/sh
'''exec' "$(dirname "$0")/%s" "$0" "$@"
' '''
# the above calls the %s interpreter in the same directory as this script
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
                head = original_file.readline().strip()
                interpreter = os.path.split(head)[-1]
                if head.startswith(b"#!/") and b"python" in interpreter:
                    # we found a Python script!
                    print("Modifying shebang for %s..." % original_filepath)
                    new_filepath = original_filepath + ".temp"
                    with open(new_filepath, 'wb') as new_file:
                        new_file.write(
                            relocatable_shebang % (interpreter, interpreter))
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
