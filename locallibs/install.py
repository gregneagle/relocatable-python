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

import os
import subprocess
import sys

PYTHON2_EXTRA_PKGS = [
    "xattr==0.6.4",
    "pyobjc",
]

PYTHON3_EXTRA_PKGS = [
    "xattr",
    "pyobjc",
]


def ensure_pip(framework_path, version="2.7"):
    '''Ensure pip is installed in our Python framework'''
    python_path = os.path.join(
        framework_path, "Versions", version, "bin/python" + version)
    if not os.path.exists(python_path):
        print >> sys.stderr, "No python at %s" % python_path
        return
    cmd = [python_path, "-m", "ensurepip"]
    print "Ensuring pip is installed..."
    print subprocess.check_output(cmd)


def install(pkgname, framework_path, version="2.7"):
    '''Use pip to install a Python pkg into framework_path'''
    python_path = os.path.join(
        framework_path, "Versions", version, "bin/python" + version)
    if not os.path.exists(python_path):
        print >> sys.stderr, "No python at %s" % python_path
        return
    cmd = [python_path, "-m", "pip", "install", pkgname]
    print "Installing %s..." % pkgname
    print subprocess.check_output(cmd)


def install_extras(framework_path, version="2.7"):
    '''install all extra pkgs into Python framework path'''
    ensure_pip(framework_path, version=version)
    if version.startswith("2."):
        for pkgname in PYTHON2_EXTRA_PKGS:
            install(pkgname, framework_path, version=version)
    if version.startswith("3."):
        for pkgname in PYTHON3_EXTRA_PKGS:
            install(pkgname, framework_path, version=version)
