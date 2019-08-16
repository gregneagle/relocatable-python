#!/usr/bin/python
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
"""Tool to build relocatable Python frameworks on macOS"""

from __future__ import print_function

import optparse

from locallibs import get
from locallibs.fix import fix_other_things
from locallibs.install import install_extras
from locallibs.relocatablizer import relocatablize


def main():
    """Main"""
    usage = "usage: %prog [options] [/path/to/framework/destination]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option(
        "--destination",
        default=".",
        help="Directory destination for the Python.framework",
    )
    parser.add_option(
        "--baseurl",
        default=get.DEFAULT_BASEURL,
        help="Override the base URL used to download the framework.",
    )
    parser.add_option(
        "--os-version",
        default=get.DEFAULT_OS_VERSION,
        help="Override the macOS version of the downloaded pkg. "
        'Current supported versions are "10.6" and "10.9". '
        "Not all Python version and macOS version combinations are valid.",
    )
    parser.add_option(
        "--python-version",
        default=get.DEFAULT_PYTHON_VERSION,
        help="Override the version of the Python framework to be downloaded. "
        "See available versions at "
        "https://www.python.org/downloads/mac-osx/",
    )
    parser.add_option(
        "--pip-requirements",
        default=None,
        help="Path to a pip freeze requirements.txt file that describes extra "
        "Python modules to be installed. If not provided, certain useful "
        "modules for macOS will be installed.",
    )
    options, _arguments = parser.parse_args()

    framework_path = get.FrameworkGetter(
        python_version=options.python_version,
        os_version=options.os_version,
        base_url=options.baseurl,
    ).download_and_extract(destination=options.destination)

    if framework_path:
        relocatablize(framework_path)
        short_version = ".".join(options.python_version.split(".")[0:2])
        install_extras(
            framework_path,
            version=short_version,
            requirements_file=options.pip_requirements,
        )
        if fix_other_things(framework_path, short_version):
            print()
            print("Done!")
            print("Customized, relocatable framework is at %s" % framework_path)


if __name__ == "__main__":
    main()
