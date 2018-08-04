#!/usr/bin/python

import os
import optparse

from locallibs import get
from locallibs.install import install_extras
from locallibs.relocatablizer import relocatablize


def main():
    '''Main'''
    usage = "usage: %prog [options] [/path/to/framework/destination]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        '--destination', default=".",
        help='Directory destination for the Python.framework')
    parser.add_option(
        '--baseurl', default=get.DEFAULT_BASEURL,
        help='Override the base URL used to download the framework.')
    parser.add_option(
        '--os-version', default=get.DEFAULT_OS_VERSION,
        help='Override the macOS version of the downloaded pkg. '
             'Current supported versions are "10.6" and "10.9". '
             'Not all Python version and macOS version combinations are valid.')
    parser.add_option(
        '--python-version', default=get.DEFAULT_PYTHON_VERSION,
        help='Override the version of the Python framework to be downloaded. '
             'See available versions at '
             'https://www.python.org/downloads/mac-osx/')
    options, arguments = parser.parse_args()

    framework_path = get.FrameworkGetter(
        python_version=options.python_version,
        os_version=options.os_version,
        base_url=options.baseurl
    ).download_and_extract(destination=options.destination)

    relocatablize(framework_path)
    short_version = ".".join(options.python_version.split(".")[0:2])
    install_extras(framework_path, version=short_version)

    print
    print "Done!"
    print "Customized, relocatable framework is at %s" % framework_path


if __name__ == '__main__':
    main()
