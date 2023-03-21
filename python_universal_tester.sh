#!/bin/bash

if [[ $1 == *"3."* ]]; then
    echo "Using Python $1" 
else
    echo "Invalid Python version"
    exit 1
fi

STATUS=0

# ensure all .so and .dylibs are universal
LIB_COUNT=$(find "Python.framework" -name "*.so" -or -name "*.dylib" | wc -l)
UNIVERSAL_COUNT=$(find "Python.framework" -name "*.so" -or -name "*.dylib" | xargs file | grep "2 architectures" | wc -l)
if [ "$LIB_COUNT" != "$UNIVERSAL_COUNT" ] ; then 
    echo "$LIB_COUNT libraries (*.so and *.dylib) found in the framework; only $UNIVERSAL_COUNT are universal!"
    echo "The following libraries are not universal:"
    find Python.framework -name "*.so" -or -name "*.dylib" | xargs file | grep -v "2 architectures" | grep -v "(for architecture"
    STATUS=1
fi

# test some more files in the framework
MORE_FILES="Python.framework/Versions/$1/Resources/Python.app/Contents/MacOS/Python
Python.framework/Versions/Current/Python
Python.framework/Versions/Current/bin/python$1"

for TESTFILE in $MORE_FILES ; do
    ARCH_TEST=$(file "$TESTFILE" | grep "2 architectures")
    if [ "$ARCH_TEST" == "" ]  ; then
        echo "$TESTFILE is not universal!"
        STATUS=1
    fi
done

[[ $STATUS == 0 ]] && echo "All files are universal!" || exit $STATUS
