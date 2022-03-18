This is a tool to make a relocatable Python framework containing PyObjC.

NOTE: while the resulting frameworks (and interpreters) have been successfully used in several projects (among them Imagr, Munki, and AutoPkg) there is no guarantee it is suitable as a general-purpose Python installation.

A relocatable Python.framework is ideal for embedding into an application's Frameworks directory, and can even be used to get PyObjC-based apps and tools running in the macOS Recovery environment, which does not include Python.

The Python version defaults to 2.7.15, and minimum (or target) macOS version is 10.9. No modules are automatically installed. Previously, the highest supported versions of pip and PyObjC are installed, as is xattr 0.6.4 (this is the version included with macOS High Sierra -- the current version has issues running in Recovery boot). To install these, use --pip-requirements=requirements_python2_recommended.txt to mimic old behavior. In previous versions of this tool on Python versions 3.x and higher, certain modules (xattr, cffi, six and pyobjc) were installed. These can be installed via --pip-requirements=requirements_python3_recommended.txt.

Currently tested versions:
    Python version 2.7.15 with macOS deployment target 10.9+
    Python version 3.7.4 with macOS deployment target 10.9+

Requires at least the command-line developer tools; might require a full Xcode install.

Basic use -- make a Python.framework in the current working directory:
./make_relocatable_python_framework.py

Specifying a target destination for the framework:
./make_relocatable_python_framework.py --destination ~/Desktop

Specifying a different Python version:
./make_relocatable_python_framework.py --python-version 3.7.4

More options:
./make_relocatable_python_framework.py --help

NOTES: 

- As of this commit: https://github.com/gregneagle/relocatable-python/commit/0184e8b43f1ecde050b07feb1761fac2f7ce0c5c, make_relocatable_python_framework.py now uses Apple's Python 3 that is included with Xcode and the Command line development tools. Python 2 was removed from macOS with the release of macOS 12.3, and make_relocatable_python_framework.py requires other tools that are included with Xcode/Command Line development tools, so this is unlikely to break anyone except perhaps those using the tool on a very out-of-date macOS and/or Xcode.

- As of this commit: https://github.com/gregneagle/relocatable-python/commit/f4c4110f36ac1cb60b8253c2e04eaf34804f7303, any signed binaries or libraries within the framework will have their signatures removed. The "relocatablizing" process modifies these files, making any signature invalid. Rather than leave an invalid signature, which might seem like potential malware (and which currently causes at least one well-known security tool to _crash_), it's better to remove the invalid signature all together.

- As of this commit: https://github.com/gregneagle/relocatable-python/commit/903c708a01d1a2444ea5648114f3acf6e7f94fd7, instead of removing the signature, we replace it with an ad-hoc signature. This is required for the code to actually run on Apple silicon.


