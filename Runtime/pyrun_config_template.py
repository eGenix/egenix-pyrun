""" eGenix PyRun Configuration Data.

    This was generated at the time eGenix PyRun was used to create the
    pyrun binary. It will not include the dynamically added or
    modified variables of the regular Python sysconfig module.

"""
import sys, os

### PyRun Configuration

# Since sysconfig.py is imported early by site.py, we cannot rely on
# pyrun_template.py to already have run, so we adjust and set the
# needed variables here.

# Copyright
pyrun_copyright = (
    "Copyright (c) 1997-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com\n"
    "Copyright (c) 2000-2012, eGenix.com Software GmbH; mailto:info@egenix.com\n"
    "All Rights Reserved.\n\n")

# Name and version
pyrun_name = '#$pyrun'
pyrun_version = '#$version'
if pyrun_version.startswith('#$'):
    pyrun_version = sys.version.split()[0]
pyrun_libversion = pyrun_version[:3]

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
