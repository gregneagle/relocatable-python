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
            os.symlink(short_version, versions_current_path)
        except OSError as err:
            print("Could not create Versions/Current symlink to %s: %s"
                  % (short_version, err), file=sys.stderr)
            return False
    return True


def fix_other_things(framework_path, short_version):
    '''Wrapper function in case there are other things we need to fix in the
    future'''
    return ensure_current_version_link(framework_path, short_version)
