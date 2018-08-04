import os
import subprocess
import sys

EXTRA_PKGS = [
    "xattr==0.6.4",
    "pyobjc",
]


def ensure_pip(framework_path, version="2.7"):
    '''Ensure pip is installed in our Python framework'''
    python_path = os.path.join(
        framework_path, "Versions", version, "bin/python")
    if not os.path.exists(python_path):
        print >> sys.stderr, "No python at %s" % python_path
        return
    cmd = [python_path, "-m", "ensurepip"]
    print "Ensuring pip is installed..."
    print subprocess.check_output(cmd)


def install(pkgname, framework_path, version="2.7"):
    '''Use pip to install a Python pkg into framework_path'''
    python_path = os.path.join(
        framework_path, "Versions", version, "bin/python")
    if not os.path.exists(python_path):
        print sys.stderr, "No python at %s" % python_path
        return
    cmd = [python_path, "-m", "pip", "install", pkgname]
    print "Installing %s..." % pkgname
    print subprocess.check_output(cmd)


def install_extras(framework_path, version="2.7"):
    '''install all extra pkgs into Python framework path'''
    ensure_pip(framework_path, version=version)
    for pkgname in EXTRA_PKGS:
        install(pkgname, framework_path, version=version)
