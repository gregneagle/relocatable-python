This is a tool to make a relocatable Python framework containing PyObjC.

A relocatable Python.framework is ideal for embedding into an application's Framework's directory, and can even be used to get PyObjC-based apps and tools running in the macOS Recovery environment, which does not include Python.

The Python version defaults to 2.7.15, and minimum (or target) macOS version is 10.9. Currently offered versions of pip and PyObjC are installed, as is xattr 0.6.4 (this is the version included with macOS High Sierra -- the current version has issues running in Recovery boot)

To-date, nothing other than the above defaults have been tested.

Basic use -- make a Python.framework in the current working directory:
./make_relocatable_python_framework

Specifying a target destination for the framework:
./make_relocatable_python_framework --destination ~/Desktop

More options:
./make_relocatable_python_framework --help

