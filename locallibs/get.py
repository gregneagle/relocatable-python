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
    
    downloaded_pkg_path = ""
    expanded_path = ""
    
    def __init__(self,
                 python_version=DEFAULT_PYTHON_VERSION,
                 os_version=DEFAULT_OS_VERSION,
                 base_url=DEFAULT_BASEURL):
        self.python_version = python_version
        self.os_version = os_version
        self.base_url = base_url
    
    def __del__(self):
        '''Clean up'''
        if self.expanded_path:
            shutil.rmtree(self.expanded_path)
        if self.downloaded_pkg_path:
            os.unlink(self.downloaded_pkg_path)

    def download(self):
        '''Downloads a macOS installer pkg from python.org.
           Returns path to the download.'''
        url = self.base_url % (
            self.python_version, self.python_version, self.os_version)
        (file_handle, destination_path) = tempfile.mkstemp()
        os.close(file_handle)
        cmd = [CURL, "-o", destination_path , url]
        print "Downloading %s..." % url
        subprocess.check_call(cmd)
        self.downloaded_pkg_path = destination_path

    def expand(self):
        '''Uses pkgutil to expand our downloaded pkg. Returns a path to the
           expanded contents.'''
        self.expanded_path = self.downloaded_pkg_path + "__expanded__"
        cmd = [PKGUTIL, "--expand",
               self.downloaded_pkg_path, self.expanded_path]
        print "Expanding %s..." % self.downloaded_pkg_path
        subprocess.check_call(cmd)

    def extract_framework(self):
        '''Extracts the Python framework from the expanded pkg'''
        payload = os.path.join(
            self.expanded_path, "Python_Framework.pkg/Payload")
        cmd = [DITTO, "-xz", payload, self.destination]
        print "Extracting %s to %s..." % (payload, self.destination)
        subprocess.check_call(cmd)

    def download_and_extract(self, destination="."):
        '''Downloads and extracts the Python framework.
           Returns path to the framework.'''
        destination = os.path.expanduser(destination)
        if os.path.basename(destination) != "Python.framework":
            destination = os.path.join(destination, "Python.framework")
        if os.path.exists(destination):
            print >> sys.stderr, "Destination %s already exists!" % destination
            return
        self.destination = destination
        self.download()
        self.expand()
        self.extract_framework()
        return destination
