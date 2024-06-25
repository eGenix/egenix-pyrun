""" Test pyrun in action.

"""
import sys
PYTHON_VERSION = sys.version_info

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
    import pickle
    if PYTHON_VERSION < (3, 0):
        # Removed/replaced in Python 3
        import cPickle
        import cStringIO
    import operator
    if PYTHON_VERSION < (3, 9):
        # Deprecated starting with Python 3.9, removed in 3.10
        import parser
    import select
    import time
    import zlib
    import mmap
    import _bisect
    import _ssl
    import _sqlite3
except ImportError as reason:
    print('%s not found.' % module_name(reason))
    if PYTHON_VERSION >= (2, 5):
        sys.exit(1)
else:
    print('done.')

print('Try loading a few Python 2.6 stdlib modules...')
try:
    import ast
    import _json
    if PYTHON_VERSION < (3, 0):
        import distutils
        import future_builtins
    if PYTHON_VERSION == (2, 6):
        # These only exist in Python 2.6 and not in 2.7
        import _fileio
        import _bytesio
except ImportError as reason:
    print('%s not found.' % module_name(reason))
    if PYTHON_VERSION >= (2, 6):
        sys.exit(1)
else:
    print('done.')

print('Try loading a few Python 2.7 stdlib modules...')
try:
    import _io
except ImportError as reason:
    print('%s not found.' % module_name(reason))
    if PYTHON_VERSION >= (2, 7):
        sys.exit(1)
else:
    print('done.')

print('Try loading a few Python 3 stdlib modules...')
try:
    import _sha3
    import html.parser
    import urllib.parse
    import typing
    if PYTHON_VERSION >= (3, 11):
        import tomllib
except ImportError as reason:
    print('%s not found.' % module_name(reason))
    if PYTHON_VERSION >= (3, 7):
        sys.exit(1)
else:
    print('done.')

# Check imports of all modules installed via Setup

# These are all modules built for Python 3.11
setup_modules = [
    '_asyncio',
    '_bisect',
    '_blake2',
    '_bz2',
    '_codecs_cn',
    '_codecs_hk',
    '_codecs_iso2022',
    '_codecs_jp',
    '_codecs_kr',
    '_codecs_tw',
    '_contextvars',
    '_crypt',
    '_csv',
    '_ctypes',
    '_curses',
    '_curses_panel',
    '_datetime',
    '_decimal',
    '_elementtree',
    '_hashlib',
    '_heapq',
    '_json',
    '_lsprof',
    '_md5',
    '_multibytecodec',
    '_multiprocessing',
    '_opcode',
    '_pickle',
    '_posixshmem',
    '_posixsubprocess',
    '_queue',
    '_random',
    '_sha1',
    '_sha256',
    '_sha3',
    '_sha512',
    '_socket',
    '_sqlite3',
    '_ssl',
    '_statistics',
    '_struct',
    '_typing', # Was added in 3.11
    '_uuid',
    #'_xxsubinterpreters', # not included in PyRun
    '_zoneinfo',
    'array',
    'audioop', # Deprecated in 3.11
    'binascii',
    'cmath',
    'fcntl',
    'grp',
    'math',
    'mmap',
    'ossaudiodev', # Deprecated in 3.11
    'pyexpat',
    'readline',
    'resource',
    'select',
    'spwd', # Deprecated in 3.11
    'syslog',
    'termios',
    'unicodedata',
    'zlib',
]
# Note: These modules were not built due to missing deps:
# _dbm                  _gdbm                 _lzma
# _tkinter              nis

print('Try loading Setup compiled Python 3.11 stdlib modules...')
for modname in setup_modules:
    try:
        __import__(modname)
    except ImportError as reason:
        print('%s not loaded: %s' % (modname, reason))
        if PYTHON_VERSION >= (3, 11):
            sys.exit(1)
print('done.')

print('Try loading ctypes (a shared mod)...')
try:
    import _ctypes
except ImportError:
    print('ctypes not found.')
else:
    print('done.')

# print('Try loading mxDateTime (a shared mod)...')
# try:
#     import mx.DateTime
# except ImportError:
#     print('mxDateTime not found.')
# else:
#     print('done.')

print('')
print('Loaded modules after test run:')
print('')
print_modules()
print('')

print('')
print('pyrun works.')
