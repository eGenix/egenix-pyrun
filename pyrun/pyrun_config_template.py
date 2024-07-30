""" eGenix PyRun Configuration Data.

    This was generated at the time eGenix PyRun was compiled.  It will
    not include the dynamically added or modified variables of the
    regular Python sysconfig module.

"""
import sys
import os

# This template is used by makepyrun.py to build the pyrun_config.py
# module used by PyRun.
#
# It uses these placeholders (all prefixed with "#$", which are filled
# in with the appropriate data by makepyrun.py:
#
# * pyrun    - name of the pyrun executable
# * version  - version of the pyrun executable (the supported Python version)
# * release  - pyrun release version
# * config   - repr() dict list of sysconfig configuration variables

### PyRun Configuration

# Since sysconfig.py is imported early by site.py, we cannot rely on
# pyrun_template.py to already have run, so we adjust and set the
# needed variables here.

# Copyright
pyrun_copyright = (
    "Copyright (c) 1997-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com\n"
    "Copyright (c) 2000-2024, eGenix.com Software GmbH; mailto:info@egenix.com\n"
    "All Rights Reserved.\n\n")

# System settings
pyrun_argv = sys.argv[:] # save original sys.argv
if not sys.executable:
    # Work around an issue in Python 3.11+ where in some cases,
    # sys.executable can be set to an empty string instead of the name
    # of the binary. Use the first entry in argv instead. See Github
    # issue #9
    if pyrun_argv:
        # The binary name will usually be in sys.argv[0]
        sys.executable = pyrun_argv[0]
    else:
        # Simply use a sane default, if all else fails
        sys.executable = 'pyrun'
pyrun_path = sys.path[:] # save original sys.path

# Name and version
pyrun_name = '#$pyrun'
pyrun_version = '#$version'
if pyrun_version.startswith('#$'):
    pyrun_version = sys.version.split()[0]
pyrun_libversion = '#$libversion'
if pyrun_libversion.startswith('#$'):
    pyrun_libversion = '.'.join(pyrun_version.split('.')[:2])
pyrun_release = '#$release'
pyrun_build = '(release %s, %s' % (
    pyrun_release,
    sys.version.split(' (', 1)[1])

# Filenames and paths
pyrun_executable = os.path.abspath(sys.executable)
if os.sep in pyrun_executable:
    pyrun_dir, pyrun_binary = pyrun_executable.rsplit(os.sep, 1)
else:
    pyrun_dir = '.'
    pyrun_binary = pyrun_executable
if os.sep in pyrun_dir:
    pyrun_prefix, pyrun_bindir = pyrun_dir.rsplit(os.sep, 1)
else:
    pyrun_prefix = pyrun_dir
    pyrun_bindir = '.'

### Update the run-time environment with the new configuration

# Correct the compile time prefix defaults; XXX Unfortunately, the C
# APIs for these will continue to return the compile time defaults
sys.executable = pyrun_executable
sys.prefix = pyrun_prefix
sys.exec_prefix = pyrun_prefix
# For Python 3 (won't hurt in Python 2)
sys.base_prefix = pyrun_prefix
sys.base_exec_prefix = pyrun_prefix

# Save the path to the pyrun binary; can also be used to detect
# running pyrun.
sys.pyrun = pyrun_binary

# Add copyright lines
sys.copyright = pyrun_copyright + sys.copyright

### Configuration data needed by Python

# Short versions of the most often needed variables
prefix = pyrun_prefix
pyrun = pyrun_binary

# Set config vars
config_vars = {
    #$config
}

### Misc configuration data

# lib2to3.refactor.get_all_fix_names()
lib2to3_fixes = (
    #$lib2to3_fixes
    )
