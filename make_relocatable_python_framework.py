#!/usr/bin/python3
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

from locallibs import get, vararg_callback
from locallibs.fix import fix_broken_signatures, fix_other_things
from locallibs.install import install_extras
from locallibs.relocatablizer import relocatablize


def main():
    """Main"""
    usage = "usage: %prog [options]"
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
        'Current supported versions are "10.6", "10.9", and "11". '
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
        "Python modules to be installed. If not provided, no modules will be installed.",
    )
    parser.add_option(
        "--no-unsign",
        dest="unsign",
        action="store_false",
        help="Do not unsign binaries and libraries after they are relocatablized."
    )
    parser.add_option(
        "--upgrade-pip",
        default=False,
        action="store_true",
        help="Upgrade pip prior to installing extra python modules."
    )
    parser.add_option(
        "--without-pip",
        default=False,
        action="store_true",
        help="Do not install pip."
    )
    parser.add_option(
        "--pip-platform", dest="pip_platform",
        action="callback", callback=vararg_callback,
        help="Specify which platform the pip should be downloaded for. "
        "Default is to the platform of the running system. "
        "Multiple values can be passed to specify multiple platforms."
    )
    parser.add_option(
        "--no-binary", dest="no_binary",
        action="callback", callback=vararg_callback,
        help="Do not use binary packages. "
        "Multiple values can be passed, and each time adds to the existing value. "
        "Accepts either ':all:' to disable all binary packages, ':none:' to empty the set "
        "(notice the colons), or one or more package names with commas between them (no colons)."
    )
    parser.add_option(
        "--only-binary", dest="only_binary",
        action="callback", callback=vararg_callback,
        help="Do not use source packages. "
        "Multiple values can be passed, and each time adds to the existing value. "
        "Accepts either ':all:' to disable all binary packages, ':none:' to empty the set "
        "(notice the colons), or one or more package names with commas between them (no colons)."
    )
    parser.set_defaults(unsign=True)
    options, _arguments = parser.parse_args()
    if options.no_binary and options.only_binary:
        parser.error("The options --no-binary and --only-binary are mutually exclusive")
    framework_path = get.FrameworkGetter(
        python_version=options.python_version,
        os_version=options.os_version,
        base_url=options.baseurl,
    ).download_and_extract(destination=options.destination)

    if framework_path:
        files_relocatablized = relocatablize(framework_path)
        if options.unsign:
            fix_broken_signatures(files_relocatablized)
        short_version = ".".join(options.python_version.split(".")[0:2])
        install_extras(
            framework_path,
            version=short_version,
            requirements_file=options.pip_requirements,
            upgrade_pip=options.upgrade_pip,
            without_pip=options.without_pip,
            pip_platform=options.pip_platform,
            no_binary=options.no_binary,
            only_binary=options.only_binary
        )
        if fix_other_things(framework_path, short_version):
            print()
            print("Done!")
            print("Customized, relocatable framework is at %s" % framework_path)


if __name__ == "__main__":
    main()
