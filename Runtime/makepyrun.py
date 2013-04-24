#!/usr/bin/env python

""" eGenix PyRun bootstrap file generator

    Usage: makepyrun <inputfile> <outputfile> <version> <libdir> <setupfile>

    Output is written to outputfile (a Python script which must be
    passed to freeze.py).

    ---------------------------------------------------------------------

    Copyright (c) 1997-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
    Copyright (c) 2000-2012, eGenix.com Software GmbH; mailto:info@egenix.com

                            All Rights Reserved.

    This software may be used under the conditions and terms of the
    eGenix.com Public License Agreement. You should have received a
    copy with this software (usually in the file LICENSE.PyRun
    located in the package's main directory). Please write to
    licenses@egenix.com to obtain a copy in case you should not have
    received a copy.

"""
#
# Note: This script is run by the temporary Python installation
# created for building pyrun. As such it has access to the
# configuration of the final pyrun executable.
#
import sys, os, re, string, pprint

### Globals

# PyRun release version
__version__ = '1.2.0'

# Python module dir
LIBDIR = os.path.split(os.__file__)[0]

# Python module Setup file
SETUPFILE = os.path.join(LIBDIR, 'config', 'Setup')

# Prefix used to build pyrun
PREFIX = os.path.abspath(os.path.join(LIBDIR, '..', '..'))

# PyRun name
PYRUN_NAME = 'pyrun'

# PyRun version
PYRUN_VERSION = sys.version.split()[0]

# PyRun release
PYRUN_RELEASE = __version__

### Configuration

# List of modules to always include
include_list = [
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
    '_sha256',
    '_sha512',
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
    #'parser',
    'pyexpat',
    ]

# List of modules to always exclude from the list of modules
exclude_list = [
    '_tkinter',
    '_ctypes_test',
    '_testcapi',
    'parser',
    ]

# List of packages to always exclude from the list of modules
exclude_package_list = [
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
    ]

# Parse a line in Modules/Setup
SETUP_LINE_RE = re.compile('^(\w+)\s+[a-zA-Z\\\\]+')

def find_builtin_modules(setupfile=SETUPFILE):

    try:
        setup = open(setupfile).readlines()
    except IOError,why:
        print 'Python Modules Setup file %s not found: %s' % (setupfile,why)
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
    except os.error, why:
        print 'Python Lib dir %s not accessible: %s' % \
              (libdir, why)
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
    files = map(lambda x: packageprefix + x[:-3], files)

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

    modules = (include_list
               + find_modules(libdir)
               + find_builtin_modules(setupfile))
    modules.sort()
    for mod in exclude_list:
        try:
            modules.remove(mod)
        except ValueError:
            pass
    return string.join(map(lambda x: 'import %s' % x, modules),'\n')

def find_module_source(modname):

    mod = __import__(modname, None, None, ['*'])
    return '%s.py' % os.path.splitext(mod.__file__)[0]

def compile_module(filename):

    """ Compile a Python module filename to .pyc and .pyo byte
        code files.

    """
    from distutils.util import byte_compile
    byte_compile([filename], optimize=0, verbose=0)
    byte_compile([filename], optimize=1, verbose=0)

def config_vars():

    if sys.version >= '2.7':
        import sysconfig
    else:
        from distutils import sysconfig
    return sysconfig.get_config_vars()

def format_template(template,
                    pyrun_name=PYRUN_NAME,
                    pyrun_version=PYRUN_VERSION,
                    pyrun_release=PYRUN_RELEASE,
                    pyrun_imports=''):

    code = template.replace('#$pyrun', pyrun_name) \
                   .replace('#$version', pyrun_version) \
                   .replace('#$release', pyrun_release) \
                   .replace('#$imports', pyrun_imports)
    return code

def patch_module(filename, find_re, replacement):

    """ Patch module file filename.

        Replaces all occurences of the RE find_re with replacement.

        The search is done in MULTILINE mode, so '^' and '$' match on
        individual lines of the file.

    """
    print 'Patching module %s' % filename
    f = open(filename, 'rb')
    mod_src = f.read()
    f.close()
    rx = re.compile(find_re, flags=re.MULTILINE)
    new_mod_src = rx.sub(replacement, mod_src)
    if new_mod_src == mod_src:
        print '*** WARNING: Module %s not changed' % filename
        return
    f = open(filename, 'wb')
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
    if sys.version >= '2.7':
        # Python 2.7 and later: sysconfig module was factored out into
        # a top-level module
        patch_module(os.path.join(libdir, 'sysconfig.py'),
                     '_CONFIG_VARS += +None',
                     'import pyrun_config; _CONFIG_VARS = pyrun_config.config_vars')
        # Unfortunately, the distutils version was kept around as well
        patch_module(os.path.join(libdir, 'distutils', 'sysconfig.py'),
                     '_config_vars += +None',
                     'import pyrun_config; _config_vars = pyrun_config.config_vars')
    else:
        # Python 2.5 and 2.6: sysconfig is a distutils package module
        patch_module(os.path.join(libdir, 'distutils', 'sysconfig.py'),
                     '_config_vars += +None',
                     'import pyrun_config; _config_vars = pyrun_config.config_vars')

def patch_site_py(libdir=LIBDIR):

    """ Patch site module.

        We disable the automatic run of main() in the site module, so
        that we can run it manually in pyrun.py.

        We also adjust the license URL to point to the PyRun license.

    """
    patch_module(os.path.join(libdir, 'site.py'),
                 '^main\(\)',
                 '#main()')
    patch_module(os.path.join(libdir, 'site.py'),
                 '"See http://www.python.org/%.3s/license.html" % sys.version',
                 '"See http://egenix.com/products/python/PyRun/license.html"')

def patch_pkgutil_py(libdir=LIBDIR):

    """ Patch pkgutil module.

        The pkgutil module doesn't know how to load the code object of
        a frozen module. As a result, running PyRun with -m module
        doesn't work for frozen modules (the -m switch uses the runpy
        module, which in return uses pkgutil).

        We add the missing support here.

    """
    module_path = os.path.join(libdir, 'pkgutil.py')
    patch_module(module_path,
                 """\
    def get_code\(self, fullname=None\):
""",                 
                 """\
    def get_code(self, fullname=None):
        if self.code is not None:
            return self.code
        fullname = self._fix_name(fullname)
        mod_type = self.etc[2]
        if mod_type == imp.PY_FROZEN:
            self.code = imp.get_frozen_object(fullname)
            return self.code
        else:
            return self._get_code(fullname)
        
    def _get_code(self, fullname=None):
""")

def create_pyrun_config_py(inputfile='pyrun_config_template.py',
                           outputfile='pyrun_config.py',
                           pyrun_name=PYRUN_NAME,
                           pyrun_version=PYRUN_VERSION,
                           pyrun_release=PYRUN_RELEASE):

    f = open(inputfile, 'rb')
    config_src = f.read()
    f.close()

    # Build config vars and replace any occurrance of the PREFIX dir
    # with a variable "prefix"
    variable_list = config_vars().items()
    variable_list.sort()
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
        elif name == 'userbase':
            repr_list.append("%r: '', # not supported" % name)
        else:
            repr_list.append('%r: %r,' % (name, value))
    config_src = config_src.replace('#$config',
                                    '\n    '.join(repr_list))

    # Add other temlate variables
    config_src = config_src.replace('#$pyrun', pyrun_name) \
                           .replace('#$version', pyrun_version) \
                           .replace('#$release', pyrun_release)

    print 'Creating module %s' % outputfile
    f = open(outputfile, 'wb')
    f.write(config_src)
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
    template = open(inputfile, 'rb').read()
    assert outputfile.endswith('.py'), 'outputfile does not end with .py'
    pyrun_name = outputfile[:-3]
    print 'Writing freeze script %s' % outputfile
    f = open(outputfile, 'wb')
    f.write(format_template(template,
                            pyrun_name=pyrun_name,
                            pyrun_version=version,
                            pyrun_release=release,
                            pyrun_imports=imports))
    f.close()
    compile_module(outputfile)

###

def main(pyrunfile='pyrun.py',
         version=sys.version[:6],
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

    # Patch sysconfig module
    patch_sysconfig_py(libdir)

    # Patch site module
    patch_site_py(libdir)

    # Patch pkgutil module
    patch_pkgutil_py(libdir)

if __name__ == '__main__':
    main(*sys.argv[1:])
    
