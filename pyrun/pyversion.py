#!/usr/local/bin/python

""" Print the Python version to stdout.

"""
# Compatible to Python 2 and 3
import sys

# Get Python version number
if '--min' in sys.argv:
    version = sys.version.split()[0][:3]
else:
    version = sys.version.split()[0]

# Add platform string
if '--platform' in sys.argv:
    from distutils.util import get_platform
    version = get_platform() + '-py' + version

# Add bits
if '--bits' in sys.argv:
    if sys.maxint > 2147483647:
        version = version + '-64bit'
    else:
        version = version + '-32bit'

# Add Unicode identifier
if '--unicode' in sys.argv:
    try:
        if sys.maxunicode > 65355:
            version = version + '_ucs4'
        else:
            version = version + '_ucs2'
    except AttributeError:
        pass

# Print result
print(version)
