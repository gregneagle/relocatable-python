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
"""Functions to pip install extra modules in our framework"""

from __future__ import print_function
from os.path import expanduser

import os
import subprocess
import sys

PYTHON2_EXTRA_PKGS = ["xattr==0.6.4", "pyobjc"]

PYTHON3_EXTRA_PKGS = ["cffi", "xattr", "pyobjc", "six"]


def ensure_pip(framework_path, version):
    """Ensure pip is installed in our Python framework"""
    python_path = os.path.join(
        framework_path, "Versions", version, "bin/python" + version
    )
    if not os.path.exists(python_path):
        print("No python at %s" % python_path, file=sys.stderr)
        return
    cmd = [python_path, "-s", "-m", "ensurepip"]
    print("Ensuring pip is installed...")
    subprocess.check_call(cmd)


def install(pkgname, framework_path, version):
    """Use pip to install a Python pkg into framework_path"""
    python_path = os.path.join(
        framework_path, "Versions", version, "bin/python" + version
    )
    if not os.path.exists(python_path):
        print("No python at %s" % python_path, file=sys.stderr)
        return
    cmd = [python_path, "-s", "-m", "pip", "install", pkgname]
    print("Installing %s..." % pkgname)
    subprocess.check_call(cmd)


def upgrade_pip_install(framework_path, version):
    """Use pip to upgrade pip"""
    python_path = os.path.join(
        framework_path, "Versions", version, "bin/python" + version
    )
    if not os.path.exists(python_path):
        print("No python at %s" % python_path, file=sys.stderr)
        return
    cmd = [python_path, "-s", "-m", "pip", "install", "--upgrade", "pip"]
    print("Upgrading pip installation...")
    subprocess.check_call(cmd)


def install_requirements(requirements_file, framework_path, version):
    """Use pip to install a Python pkg into framework_path"""
    python_path = os.path.join(
        framework_path, "Versions", version, "bin/python" + version
    )
    if not os.path.exists(python_path):
        print("No python at %s" % python_path, file=sys.stderr)
        return
    if version.startswith("3.9"):
        # nasty hack to get xattr to install under 3.9.1rc1
        with open(requirements_file) as rfile:
            if "xattr" in rfile.read():
                install("cffi", framework_path, version)
    cmd = [python_path, "-s", "-m", "pip", "install", "-r", requirements_file]
    print("Installing modules from %s..." % requirements_file)
    subprocess.check_call(cmd)


def install_extras(framework_path, version="2.7", requirements_file=None,
                   install_wheel=False, upgrade_pip=False):
    """install all extra pkgs into Python framework path"""
    print()
    python_guard_path = expanduser("~/Library/Python/%s") % version
    if os.path.exists(python_guard_path):
        print('*********************************************************')
        print('*** Python user files exist that conflict with the    ***')
        print('*** version of relocatable python you are trying to   ***')
        print('*** create. This will likely result in site-packages  ***')
        print('*** that are not installed or out-of-date. Please     ***')
        print('*** remove these files or create this package on a    ***')
        print('*** clean computer. The files are located at:         ***')
        print('*** %s ***' % python_guard_path)
        print('*********************************************************')
        print()
    ensure_pip(framework_path, version)
    if upgrade_pip:
        upgrade_pip_install(framework_path, version)
    if install_wheel:
        install("wheel", framework_path, version)
    if requirements_file:
        install_requirements(requirements_file, framework_path, version)
    elif version.startswith("2."):
        for pkgname in PYTHON2_EXTRA_PKGS:
            print()
            install(pkgname, framework_path, version)
    elif version.startswith("3."):
        for pkgname in PYTHON3_EXTRA_PKGS:
            print()
            install(pkgname, framework_path, version)
