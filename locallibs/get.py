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
"""Object to download the Python.org framework pkg and extract it"""

from __future__ import print_function

import os
import shutil
import subprocess
import sys
import tempfile

CURL = "/usr/bin/curl"
DITTO = "/usr/bin/ditto"
PKGUTIL = "/usr/sbin/pkgutil"
DEFAULT_BASEURL = "https://www.python.org/ftp/python/%s/python-%s-macosx%s.pkg"
DEFAULT_PYTHON_VERSION = "2.7.15"
DEFAULT_OS_VERSION = "10.9"


class FrameworkGetter(object):
    """Handles getting the Python.org pkg and extracting the framework"""

    downloaded_pkg_path = ""
    expanded_path = ""

    def __init__(
        self,
        python_version=DEFAULT_PYTHON_VERSION,
        os_version=DEFAULT_OS_VERSION,
        base_url=DEFAULT_BASEURL,
    ):
        self.python_version = python_version
        self.os_version = os_version
        self.base_url = base_url
        self.destination = ""

    def __del__(self):
        """Clean up"""
        if self.expanded_path:
            shutil.rmtree(self.expanded_path)
        if self.downloaded_pkg_path:
            os.unlink(self.downloaded_pkg_path)

    def download(self):
        """Downloads a macOS installer pkg from python.org.
           Returns path to the download."""
        if self.base_url == DEFAULT_BASEURL and \
           not self.os_version.startswith('10'):
            base_url = self.base_url.replace('macosx', 'macos')
        else:
            base_url = self.base_url
        url = base_url % (
            self.python_version,
            self.python_version,
            self.os_version,
        )
        (file_handle, destination_path) = tempfile.mkstemp()
        os.close(file_handle)
        cmd = [CURL, "--fail", "-o", destination_path, url]
        print("Downloading %s..." % url)
        subprocess.check_call(cmd)
        self.downloaded_pkg_path = destination_path

    def expand(self):
        """Uses pkgutil to expand our downloaded pkg. Returns a path to the
           expanded contents."""
        self.expanded_path = self.downloaded_pkg_path + "__expanded__"
        cmd = [
            PKGUTIL,
            "--expand",
            self.downloaded_pkg_path,
            self.expanded_path,
        ]
        print("Expanding %s..." % self.downloaded_pkg_path)
        subprocess.check_call(cmd)

    def extract_framework(self):
        """Extracts the Python framework from the expanded pkg"""
        payload = os.path.join(
            self.expanded_path, "Python_Framework.pkg/Payload"
        )
        cmd = [DITTO, "-xz", payload, self.destination]
        print("Extracting %s to %s..." % (payload, self.destination))
        subprocess.check_call(cmd)

    def download_and_extract(self, destination="."):
        """Downloads and extracts the Python framework.
           Returns path to the framework."""
        destination = os.path.expanduser(destination)
        if os.path.basename(destination) != "Python.framework":
            destination = os.path.join(destination, "Python.framework")
        if os.path.exists(destination):
            print(
                "Destination %s already exists!" % destination, file=sys.stderr
            )
            return None
        self.destination = destination
        try:
            self.download()
            self.expand()
            self.extract_framework()
            return destination
        except subprocess.CalledProcessError as err:
            sys.exit("%s" % err)
