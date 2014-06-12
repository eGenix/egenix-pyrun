""" Test pyrun in action.

"""
import sys

PYTHON_VERSION = sys.version[:3]

def module_name(err):
    return str(err).split()[-1]

def print_modules():
    loaded_modules = sorted(sys.modules.items())
    for name, mod in loaded_modules:
        print('Module %-20s: %r' % (name, mod))

print('Using pyrun executable from:')
print('')
print(sys.executable)
print('')

print('Loaded modules after startup:')
print('')
print_modules()
print('')
print('sys.path after startup:')
print('')
print(sys.path)
print('')

print('Try loading a few Python 2.5 stdlib modules...')
try:
    import os
    import datetime
    import socket
    import pyexpat
    import xml.etree
    import urllib
    import email
    import email.generator
    import email.charset
    import unicodedata
    import locale
    import itertools
    import random
    import _ssl
    import math
    import cmath
    import collections
    import weakref
    import array
    import binascii
    import bz2
    if PYTHON_VERSION < '3':
        import cPickle
        import cStringIO
    import operator
    import parser
    import select
    import time
    import zlib
    import mmap
    import _bisect
    import _ssl
except ImportError as reason:
    print('%s not found.' % module_name(reason))
    if PYTHON_VERSION >= '2.5':
        sys.exit(1)
else:
    print('done.')

print('Try loading a few Python 2.6 stdlib modules...')
try:
    import ast
    import _json
    import lib2to3
    import lib2to3.pygram
    if PYTHON_VERSION < '3':
        import future_builtins
    if PYTHON_VERSION == '2.6':
        # These only exist in Python 2.6 and not in 2.7
        import _fileio
        import _bytesio
except ImportError as reason:
    print('%s not found.' % module_name(reason))
    if PYTHON_VERSION >= '2.6':
        sys.exit(1)
else:
    print('done.')

print('Try loading a few Python 2.7 stdlib modules...')
try:
    import _io
except ImportError as reason:
    print('%s not found.' % module_name(reason))
    if PYTHON_VERSION >= '2.7':
        sys.exit(1)
else:
    print('done.')

print('Try loading ctypes (a shared mod)...')
try:
    import _ctypes
except ImportError:
    print('ctypes not found.')
else:
    print('done.')

print('Try loading mxDateTime (a shared mod)...')
try:
    import mx.DateTime
except ImportError:
    print('mxDateTime not found.')
else:
    print('done.')

print('')
print('Loaded modules after test run:')
print('')
print_modules()
print('')

print('')
print('pyrun works.')
