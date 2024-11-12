#!/usr/bin/env python

""" eGenix PyRun bootstrap file generator

    Usage: makepyrun <inputfile> <outputfile> <version> <libdir> <setupfile>

    Output is written to outputfile (a Python script which must be
    passed to freeze.py).

    ---------------------------------------------------------------------

    Copyright (c) 1997-2000, IKDS Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2024, eGenix.com Software GmbH; mailto:info@egenix.com

                            All Rights Reserved.

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""
# Compatible to Python 2.7 and 3.7+

#
# Note: This script is run by the temporary Python installation
# created for building pyrun. As such it has access to the
# configuration of the final pyrun executable.
#
import sys
import os
import re

try:
    # sysconfig was added to Python 2.7 as top-level module
    import sysconfig
except ImportError:
    # In Python 2.6 it's still part of the distutils package
    from distutils import sysconfig

### Globals

# PyRun release version
#
# Keep this in sync with the PACKAGEVERSION in the top-level Makefile
#
__version__ = '2.6.0'

# Debug level
_debug = 1

# File encoding to use
ENCODING = 'utf-8'

# Python version flags
PY2 = (sys.version_info[0] == 2)
PY3 = (sys.version_info[0] == 3)
PY310GE = (sys.version_info[:2] >= (3, 10))
PY311 = (sys.version_info[:2] == (3, 11))
PY311GE = (sys.version_info[:2] >= (3, 11))
PY312 = (sys.version_info[:2] == (3, 12))
PY312GE = (sys.version_info[:2] >= (3, 12))

# Python module dir
LIBDIR = sysconfig.get_config_var('LIBDEST')

# Python build dir
BUILDDIR = sysconfig.get_config_vars().get(
    'abs_builddir',
    os.path.abspath(os.environ.get('PYTHONDIR', '')))

# Python module Setup file
if PY311GE:
    # Starting with Python 3.11, we're using the Setup.local as our
    # custom Setup file
    SETUPFILE = os.path.join(sysconfig.get_config_var('LIBPL'), 'Setup.local')
else:
    SETUPFILE = os.path.join(sysconfig.get_config_var('LIBPL'), 'Setup')

# Prefix used for building pyrun; this is replaced in pyrun_config.py
# with logic to dynamically determine the prefix at runtime.
PREFIX = os.path.abspath(os.path.join(LIBDIR, '..', '..'))

# PyRun name
PYRUN_NAME = 'pyrun'

# PyRun Python version
PYRUN_VERSION = sys.version.split()[0]

# PyRun release
PYRUN_RELEASE = __version__

### Python 2 vs. 3

if PY2:
    # Use the codec.open function instead of the builtin open
    def open(filename, mode, encoding=ENCODING):
        import codecs
        return codecs.open(filename, mode, encoding=encoding)

    import cPickle as pickle

else:
    import pickle

### Configuration

# List of modules to always include (even if they are not found
# by the module finder)
include_list = [
    # Python 2
    '_bisect',
    '_bsddb',
    '_bytesio',
    #'_codecs_cn'
    #'_codecs_hk'
    #'_codecs_iso2022'
    #'_codecs_jp'
    #'_codecs_kr'
    #'_codecs_tw',
    '_collections',
    '_ctypes',
    '_curses'
    '_curses_panel',
    '_elementtree',
    '_fileio',
    '_functools',
    '_hashlib',
    '_heapq',
    #'_hotshot',
    #'_lsprof',
    #'_multibytecodec',
    '_scproxy',
    '_sha',
    '_sqlite3',
    #'_subprocess',
    #'audioop',
    'bz2',
    'collections',
    'ctypes',
    'datetime',
    'dbm',
    'future_builtins',
    'hashlib',
    'math',
    'cmath',
    'resource',
    'syslog',
    #'parser',
    'pyexpat',
    # Python 3
    #
    # Note: Adding _lzma can cause serious issues, since the needed lib
    # isn't universally installed everywhere.  See #1793 and #1794.
    #'_lzma',
    ]

# The SHA modules were renamed in 3.12; SHA3 was added in Python 3
if PY312GE:
    include_list.extend([
        '_sha2',
        '_sha3',
    ])
elif PY3:
    include_list.extend([
        '_sha256',
        '_sha512',
        '_sha3',
    ])
else:
    include_list.extend([
        '_sha256',
        '_sha512',
    ])

# List of modules to always exclude from the list of modules
#
# Note: These modules are only excluded from the generated
# pyrun.py. freeze.py may still find them being imported from other
# modules, so you may also have to exclude them explicitly in the
# freeze.py call (see EXCLUDES in the top-level Makefile)
#
exclude_list = [
    # Python 2
    'Tkinter',
    '_tkinter',
    'turtle',
    '_ctypes_test',
    '_testcapi',
    'parser',
    'crypt',
    'tabnanny',
    # Python 2 + 3
    '_pyio', # the Python version of the io module
    ]

if PY3:
    # Only exclude in Python 3
    exclude_list.extend([
        # - none so far
    ])

if PY311GE:
    # Only exclude in Python 3.11+
    exclude_list.extend([
        'asynchat',
        'asyncore',
        'smtpd',
    ])

if PY311:
    # Only exclude in Python 3.11:
    #
    # These modules are deepfrozen in Python 3.11, so don't include them
    # as frozen modules as well.
    #
    exclude_list.extend([
        'abc',
        'codecs',
        '_collections_abc',
        'frozen_only',
        'genericpath',
        'getpath',
        '__hello__',
        'importlib._bootstrap_external',
        'importlib._bootstrap',
        'importlib.machinery',
        'importlib.util',
        'io',
        'ntpath',
        'os',
        '__phello__',
        '__phello__.ham.eggs',
        '__phello__.ham',
        '__phello__.spam',
        'posixpath',
        'runpy',
        '_sitebuiltins',
        'site',
        'stat',
        'zipimport',
    ])

# List of packages to always exclude from the list of modules
#
# Note: These packages are only excluded from the generated
# pyrun.py. freeze.py may still find them being imported from other
# modules, so you may also have to exclude them explicitly in the
# freeze.py call (see EXCLUDES in the top-level Makefile)
#
exclude_package_list = [
    # Python 2
    'test',
    'idlelib',
    'compiler',
    'bsddb.test',
    'ctypes.test',
    'distutils.tests',
    'email.test',
    'sqlite3.test',
    'json.tests',
    'lib2to3.tests',
    'unittest.test',
    'pydoc_data',
    # Python 3
    'tkinter',
    'turtledemo',
    'setuptools',
    'pip',
    'ensurepip', # ensurepip needs access to bundled whl files; see #1774
    ]

if PY310GE:
    # Only exclude in Python 3.10+
    exclude_package_list.extend([
        # lib2to3 is not needed for modern Python 3 code anymore. If
        # still needed for development, please add as dev dependency to
        # your app
        'lib2to3',
        # distutils is deprecated as stdlib package. Please use the
        # setuptools' provided version instead
        'distutils',
    ])

# Parse a line in Modules/Setup
SETUP_LINE_RE = re.compile('^(\w+)\s+[a-zA-Z\\\\]+')

def find_builtin_modules(setupfile=SETUPFILE):

    try:
        setup = open(setupfile, 'r', encoding=ENCODING).readlines()
    except IOError as why:
        print('Python Modules Setup file %s not found: %s' % (setupfile,why))
        sys.exit(1)
    modules = []
    for line in setup:
        m = SETUP_LINE_RE.match(line)
        if m:
            module = m.group(1)
            if module[-6:] == 'module':
                module = module[:-6]
            modules.append(module)
    return modules

def find_modules(libdir=LIBDIR, recurse=1, packageprefix=''):

    # Scan files in libdir
    try:
        files = os.listdir(libdir)
    except os.error as why:
        print('Python Lib dir %s not accessible: %s' % \
              (libdir, why))
        sys.exit(1)

    # Find package dirs
    packages = []
    for file in files:
        pathname = os.path.join(libdir, file)
        if os.path.isdir(pathname) and \
           os.path.exists(os.path.join(pathname, '__init__.py')):
            packages.append(file)

    # Filter out .py files
    files = filter(lambda x: x[-3:] == '.py', files)
    files = [packageprefix + x[:-3] for x in files]

    # Recurse into packages
    if recurse:
        for package in packages:
            packagename = packageprefix + package
            if packagename in exclude_package_list:
                continue
            files.append(packagename)
            pkgdir = os.path.join(libdir, package)
            files.extend(find_modules(pkgdir, recurse,
                                      packagename + '.'))

    return files

def find_imports(libdir=LIBDIR, setupfile=SETUPFILE):

    modules = sorted((include_list
               + find_modules(libdir)
               + find_builtin_modules(setupfile)))
    for mod in exclude_list:
        try:
            modules.remove(mod)
        except ValueError:
            pass
    return '\n'.join(('import %s' % mod
                      for mod in modules))

def find_module_source(modname):

    mod = __import__(modname, None, None, ['*'])
    return '%s.py' % os.path.splitext(mod.__file__)[0]

def compile_module(filename):

    """ Byte compile a Python module filename to .pyc/.pyo files.

        Files for all supported optimization levels are generated (0-2).

    """
    if PY3:
        import compileall
        for optimize in (0, 1, 2):
            compileall.compile_file(
                filename,
                quiet=1,
                optimize=optimize,
            )
    else:
        # For Python 2 it's better to use distutils, since this supports
        # generating optimized files with different levels than the
        # running Python interpreter
        from distutils.util import byte_compile
        for optimize in (0, 1, 2):
            byte_compile([filename], optimize=optimize, verbose=0)

def config_vars():

    if sys.version >= '2.7':
        import sysconfig
    else:
        from distutils import sysconfig
    return sysconfig.get_config_vars()

def format_template(template, **kws):

    code = template
    for name, value in kws.items():
        code = code.replace('#$%s' % name, value)
    return code

def patch_module(filename, find_re, replacement, flags=re.MULTILINE):

    """ Patch module file filename.

        Replaces all occurences of the RE find_re with replacement.

        The search is done using flags as re flags. flags defaults to
        re.MULTILINE mode, so '^' and '$' match on individual lines of
        the file.

    """
    print('Patching module %s' % filename)
    f = open(filename, 'r', encoding=ENCODING)
    mod_src = f.read()
    f.close()
    rx = re.compile(find_re, flags=flags)
    new_mod_src = rx.sub(replacement, mod_src)
    if new_mod_src == mod_src:
        print('*** WARNING: Module %s not changed' % filename)
        return
    f = open(filename, 'w', encoding=ENCODING)
    f.write(new_mod_src)
    f.close()
    compile_module(filename)

def patch_sysconfig_py(libdir=LIBDIR):

    """ Patch configuration into sysconfig module.

        Unfortunately, there's no other way to get the data into the
        module, other than hacking the global cache used by the module
        for storing the already parsed values.

        Note: We don't support the os.environ variable ARCHFLAGS on
        Mac OS X as the original sysconfig does, since we hardcode the
        config settings into the module, so the setup code is not run
        when calling get_config_vars().

    """
    if sys.version_info >= (2, 7):
        # Python 2.7 and later: sysconfig module was factored out into
        # a top-level module
        patch_module(os.path.join(libdir, 'sysconfig.py'),
                     '_CONFIG_VARS += +None',
                     'import pyrun_config; _CONFIG_VARS = pyrun_config.config_vars')
        # Unfortunately, the distutils version was kept around as well
        if not PY310GE:
            patch_module(os.path.join(libdir, 'distutils', 'sysconfig.py'),
                         '_config_vars += +None',
                         'import pyrun_config; _config_vars = pyrun_config.config_vars')
        # Disable is_python_build() check during startup.
        patch_module(os.path.join(libdir, 'sysconfig.py'),
                     '_PYTHON_BUILD += +is_python_build\(.*\)',
                     '_PYTHON_BUILD = False')
    else:
        # Python 2.5 and 2.6: sysconfig is a distutils package module
        patch_module(os.path.join(libdir, 'distutils', 'sysconfig.py'),
                     '_config_vars += +None',
                     'import pyrun_config; _config_vars = pyrun_config.config_vars')

def patch__sysconfigdata_py(libdir=LIBDIR):

    """ Patch the new _sysconfigdata module in Python 2.7 and 3.4.

    """
    module_name = '_sysconfigdata.py'
    if sys.version_info >= (3, 6):
        # In Python 3.6, the module name was changed to include ABI,
        # platform and architecture details, so we have to fetch the name
        # from an internal function in sysconfig.  If this internal function
        # is changed, adapt this code as necessary:
        import sysconfig
        module_name = sysconfig._get_sysconfigdata_name() + '.py'
    if sys.version_info >= (2, 7, 5) or sys.version_info >= (3, 3):
        # Python 2.7.5 and later, 3.3 and later: the build time config
        # data was stored into a new private module _sysconfigdata.py
        patch_module(os.path.join(libdir, module_name),
                     'build_time_vars += +{.+}',
                     'import pyrun_config; build_time_vars = pyrun_config.config_vars',
                     flags=re.DOTALL)

def patch_site_py(libdir=LIBDIR):

    """ Patch site module.

        We disable the automatic run of main() in the site module, so
        that we can run it manually in pyrun.py.

        We also adjust the license URL to point to the PyRun license.

    """
    # Disable automatic run of main()
    patch_module(
        os.path.join(libdir, 'site.py'),
        '^( *)main\(\)',
        '\\1pass #main()')
    # Adjust license file name
    patch_module(
        os.path.join(libdir, 'site.py'),
        '"LICENSE[.a-zA-Z]*"',
        '"LICENSE.eGenix-PyRun"')
    # Add license URL
    patch_module(
        os.path.join(libdir, 'site.py'),
        '('
        '"See https?://www\.python\.org[^"]*/license(\.html)?" % sys\.version|'
        '"See https?://www\.python\.org[^"%]*/license/?"'
        ')',
        '"See https://pyrun.org/license.html"')
    # Disable use of lib/site-python (removed in Python 3.5)
    if sys.version_info < (3, 5):
        patch_module(
            os.path.join(libdir, 'site.py'),
            'sitepackages.append\(os.path.join\(prefix, "lib", "site-python"\)\)',
            '#sitepackages.append(os.path.join(prefix, "lib", "site-python"))')
    # Disable ENABLE_USER_SITE, since we don't want PyRun to install
    # things in the user's site-packages dir
    patch_module(
        os.path.join(libdir, 'site.py'),
        'ENABLE_USER_SITE = None',
        'ENABLE_USER_SITE = False')

def patch_ssl_py(libdir=LIBDIR):

    """ Patch ssl module.

        We add support for the PYRUN_HTTPSVERIFY OS environment
        variable.

    """
    # Add support for PYRUN_HTTPSVERIFY
    patch_module(
        os.path.join(libdir, 'ssl.py'),
        '^_create_default_https_context = create_default_context',
        "#_create_default_https_context = create_default_context\n"
        "if int(os.environ.get('PYRUN_HTTPSVERIFY', 1)):\n"
        "    _create_default_https_context = create_default_context\n"
        "else:\n"
        "    _create_default_https_context = _create_unverified_context\n"
        )

# This is no longer needed for Python 3.10+, since we're no longer
# including lib2to3 in PyRun.
def patch_lib2to3_pygram(libdir=LIBDIR):

    """ Patch lib2to3.pygram module.

        We load the grammars from the pyrun_grammar module.

    """
    patch_module(
        os.path.join(libdir, 'lib2to3', 'pygram.py'),
        '^python_grammar = driver.load_packaged_grammar\("lib2to3", _GRAMMAR_FILE\)',
        '#python_grammar = driver.load_packaged_grammar("lib2to3", _GRAMMAR_FILE)\n'
        "import pyrun_grammar\n"
        "python_grammar = pyrun_grammar.load_python_grammar()\n"
        )
    patch_module(
        os.path.join(libdir, 'lib2to3', 'pygram.py'),
        '^pattern_grammar = driver.load_packaged_grammar\("lib2to3", _PATTERN_GRAMMAR_FILE\)',
        '#pattern_grammar = driver.load_packaged_grammar("lib2to3", _PATTERN_GRAMMAR_FILE)\n'
        "pattern_grammar = pyrun_grammar.load_pattern_grammar()\n"
        )

def create_pyrun_config_py(inputfile='pyrun_config_template.py',
                           outputfile='pyrun_config.py',
                           pyrun_name=PYRUN_NAME,
                           pyrun_version=PYRUN_VERSION,
                           pyrun_release=PYRUN_RELEASE):

    f = open(inputfile, 'r', encoding=ENCODING)
    template = f.read()
    f.close()

    # Build config vars and replace any occurrence of the PREFIX dir
    # with a variable "prefix"
    variable_list = sorted(config_vars().items())
    repr_list = []
    for name, value in variable_list:
        if not isinstance(value, str):
            repr_list.append('%r: %r,' % (name, value))
        elif value.startswith(PREFIX) and PREFIX not in value[1:]:
            value = value[len(PREFIX):]
            if value:
                repr_list.append('%r: prefix + %r,' % (name, value))
            else:
                repr_list.append('%r: prefix,' % name)
        elif PREFIX in value:
            value = value.replace('%', '%%').replace(PREFIX, '%(prefix)s')
            repr_list.append('%r: %r %% globals(),' % (name, value))
        elif value.startswith(BUILDDIR):
            # Since the pyrun build dir will most likely not be
            # available at runtime, we point the settings to a most
            # likely non-existing directory.
            value = '/pyrun-build-dir' + value[len(BUILDDIR):]
            repr_list.append('%r: %r, # dir does not exist' % (name, value))
        elif name == 'userbase':
            repr_list.append("%r: '', # userbase is not supported by pyrun" %
                             name)
        else:
            repr_list.append('%r: %r,' % (name, value))


    # Build list of included lib2to3 fixers
    if not PY310GE:
        # Only supported in Python 2 build of PyRun
        import lib2to3.refactor
        fixes = lib2to3.refactor.get_all_fix_names('lib2to3.fixes')
    else:
        fixes = []

    # Add other template variables
    print('Creating module %s' % outputfile)
    f = open(outputfile, 'w', encoding=ENCODING)
    f.write(format_template(template,
                            config='\n    '.join(repr_list),
                            pyrun=pyrun_name,
                            version=pyrun_version,
                            libversion='.'.join(pyrun_version.split('.')[:2]),
                            release=pyrun_release,
                            lib2to3_fixes=repr(fixes)))
    f.close()
    compile_module(outputfile)

# This is no longer needed for Python 3.10+, since we're no longer
# including lib2to3 in PyRun.
def create_pyrun_grammar_py(inputfile='pyrun_grammar_template.py',
                            outputfile='pyrun_grammar.py'):

    f = open(inputfile, 'r', encoding=ENCODING)
    template = f.read()
    f.close()

    # Build grammar
    import lib2to3.pygram
    python_grammar_pickle = pickle.dumps(
        lib2to3.pygram.python_grammar)
    pattern_grammar_pickle = pickle.dumps(
        lib2to3.pygram.pattern_grammar)

    print('Creating module %s' % outputfile)
    f = open(outputfile, 'w', encoding=ENCODING)
    f.write(format_template(template,
                            python_grammar_pickle=repr(python_grammar_pickle),
                            pattern_grammar_pickle=repr(pattern_grammar_pickle)))
    f.close()
    compile_module(outputfile)

def create_pyrun_py(inputfile='pyrun_template.py',
                    outputfile='pyrun.py',
                    version=PYRUN_VERSION,
                    release=PYRUN_RELEASE,
                    libdir=LIBDIR,
                    setupfile=SETUPFILE):

    """ Create a pyrun.py freeze file from a template.

    """
    imports = find_imports(libdir, setupfile)
    f = open(inputfile, 'r', encoding=ENCODING)
    template = f.read()
    f.close()

    assert outputfile.endswith('.py'), 'outputfile does not end with .py'
    pyrun_name = outputfile[:-3]

    print('Writing freeze script %s' % outputfile)
    f = open(outputfile, 'w', encoding=ENCODING)
    f.write(format_template(template,
                            pyrun=pyrun_name,
                            version=version,
                            release=release,
                            imports=imports))
    f.close()
    compile_module(outputfile)

###

def main(pyrunfile='pyrun.py',
         version=PYRUN_VERSION,
         libdir=LIBDIR,
         setupfile=SETUPFILE):

    # Create pyrun.py script
    create_pyrun_py(inputfile='pyrun_template.py',
                    outputfile=pyrunfile,
                    version=version,
                    libdir=libdir,
                    setupfile=setupfile)

    # Create pyrun_config module
    create_pyrun_config_py(inputfile='pyrun_config_template.py',
                           outputfile=os.path.join(libdir, 'pyrun_config.py'))

    # Create pyrun_grammar module
    if not PY310GE:
        # Only supported in Python 2 builds of PyRun
        create_pyrun_grammar_py(inputfile='pyrun_grammar_template.py',
                                outputfile=os.path.join(libdir, 'pyrun_grammar.py'))

    # Patch sysconfig module
    patch_sysconfig_py(libdir)

    # Patch _sysconfigdata module (if needed)
    patch__sysconfigdata_py(libdir)

    # Patch site module
    patch_site_py(libdir)

    # Patch ssl module
    patch_ssl_py(libdir)

    # Patch lib2to3.pygram
    if not PY310GE:
        # Only supported in Python 2 builds of PyRun
        patch_lib2to3_pygram(libdir)

if __name__ == '__main__':
    main(*sys.argv[1:])

