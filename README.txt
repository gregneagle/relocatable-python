This is a tool to make a relocatable Python framework containing PyObjC.

NOTE: while the resulting frameworks (and interpreters) have been successfully used in several projects (among them Imagr, Munki, and AutoPkg) there is no guarantee it is suitable as a general-purpose Python installation.

A relocatable Python.framework is ideal for embedding into an application's Frameworks directory, and can even be used to get PyObjC-based apps and tools running in the macOS Recovery environment, which does not include Python.

The Python version defaults to 2.7.15, and minimum (or target) macOS version is 10.9. Currently offered versions of pip and PyObjC are installed, as is xattr 0.6.4 (this is the version included with macOS High Sierra -- the current version has issues running in Recovery boot)

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

NOTE: as of this commit: https://github.com/gregneagle/relocatable-python/commit/f4c4110f36ac1cb60b8253c2e04eaf34804f7303, any signed binaries or libraries within the framework will have their signatures removed. The "relocatablizing" process modifies these files, making any signature invalid. Rather than leave an invalid signature, which might seem like potential malware (and which currently causes at least one well-known security tool to _crash_), it's better to remove the invalid signature all together.


