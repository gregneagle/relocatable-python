This is a tool to make a relocatable Python framework containing PyObjC.

Python version defaults to 2.7.15, and minimum macOS version is 10.9. Currently offered versions of pip, xattr, and PyObjC are installed.

To-date, nothing other than the above defaults have been tested.

Basic use -- make a Python.framework in the current working directory:
./make_relocatable_python_framework

Specifying a target destination for the framework:
./make_relocatable_python_framework --destination ~/Desktop

More options:
./make_relocatable_python_framework --help

