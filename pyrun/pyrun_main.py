#===========================================================================
#
# PyRun main startup code
#
#---------------------------------------------------------------------------
#
# This file provides the startup code for PyRun and is used by the
# bootloader code.
#
# IMPORTANT:
#
# All variables you add to this namespace will end up in the globals()
# namespace of the script that's being run.
#
# Compatible to Python 2.7 and 3.4+

### Imports

import sys
import os
import pyrun_config
from pyrun_config import (
    pyrun_name,
    pyrun_version,
    pyrun_libversion,
    pyrun_release,
    pyrun_build,
    pyrun_copyright,
    pyrun_executable,
    pyrun_dir,
    pyrun_binary,
    pyrun_prefix,
    pyrun_bindir,
    )

### Globals

# PyRun properties (set in pyrun_main() below)
pyrun_mode = 'script'
pyrun_app = 'pyrun'

# Settings
pyrun_argv = sys.argv[:] # save original sys.argv

# Options
pyrun_verbose = int(os.environ.get('PYRUN_VERBOSE', 0))
pyrun_debug = int(os.environ.get('PYRUN_DEBUG', 0))
pyrun_as_module = False
pyrun_as_string = False
pyrun_bytecode = False
pyrun_ignore_environment = False
pyrun_ignore_pth_files = False
pyrun_skip_site_main = False
pyrun_skip_user_site = False
pyrun_safe_path = int(os.environ.get('PYTHONSAFEPATH', 0))
pyrun_inspect = int(os.environ.get('PYTHONINSPECT', 0))
pyrun_unbuffered = int(os.environ.get('PYTHONUNBUFFERED', 0))
pyrun_optimized = int(os.environ.get('PYTHONOPTIMIZE', 0))
pyrun_dontwritebytecode = False

### Python 2 vs. 3

# Runtime flags
PY2 = (sys.version_info[0] == 2)
PY3 = (sys.version_info[0] == 3)

if PY3:
    # Python 3 and above can use the exec() function; in Python 2 "exec" is
    # a keyword, we have to use the odd getattr() below.
    import builtins
    pyrun_exec_code = getattr(builtins, 'exec')

    # Python 3 does not include the execfile() builtin
    def pyrun_exec_code_file(filename, globals_dict, locals_dict=None):
        with open(filename, 'r', encoding='utf-8') as file:
            source = file.read()
        code = compile(source, filename, 'exec', optimize=pyrun_optimized)
        pyrun_exec_code(code, globals_dict, locals_dict)

    # Python 3 no longer has raw_input(). Use input() instead
    raw_input = input

else:
    # Emulate Python 3 exec() function in Python 2
    def pyrun_exec_code(code, globals_dict, locals_dict=None):
        if locals_dict is None:
            locals_dict = globals_dict
        exec('exec code in globals_dict, locals_dict')

    # We can use execfile() in Python 2
    pyrun_exec_code_file = execfile

### Helpers

def pyrun_update_runtime():

    """ Update the run-time environment after the changes made
        in pyrun_config.py.

    """
    # Reset site settings
    if 'site' in sys.modules:
        import site
        site.PREFIXES = [sys.prefix]
        site.setcopyright()

def pyrun_banner():

    """ Return the banner text to display when starting up pyrun without
        any command line options.

    """
    return (
        'eGenix PyRun %s %s\n'
        'Thank you for using eGenix PyRun. Type "help" or "license" for details.\n'
        % (pyrun_version,
           pyrun_build))

def pyrun_help(extra_lines=()):

    """ Write help text to stderr.

        extra_lines are shown under the help text.

    """
    # Format the help text
    help_text = ("""\
Usage: %s [pyrunoptions] [<script>] [parameters]

Version: %s %s

Available PyRun command line options:

-b:       run the given <script> file as bytecode
-c:       compile and run <script> directly as Python code
-d:       enable debug mode (-dd for level 2)
-h:       show this help text
-i:       enable interactive inspection mode
-m:       import and run a module <script> available on PYTHONPATH
-s:       ignore user site
-u:       open stdout/stderr in unbuffered mode
-v:       run in verbose mode (-vv for level 2)
-B:       don't write byte code files
-E:       ignore environment variables (only PYTHONPATH)
-I:       isolate from environment: same as -E -s
-O:       run in optimized mode (-OO also removes doc-strings)
-P:       don't add script or current dir to sys.path
-R:       not implemented; use PYTHONHASHSEED instead
-S:       skip running site.main() and disable support for .pth files
-V:       print the pyrun version and exit
-W arg:   add arg as warning filter
-3:       not implemented; only for compatibility with Python
-X arg:   not implemented; only for compatibility with Python

Most Python environment variables are supported.

Without options, the given <script> file is loaded and run. Parameters
are passed to the script via sys.argv as normal.

Interactive mode is started, if no <script> file is given.

""" % (pyrun_name,
       pyrun_version,
       pyrun_build)).splitlines()
    if extra_lines:
        help_text.extend(extra_lines)
    for line in help_text:
        sys.stderr.write('%s\n' % line)

def pyrun_info(extra_lines=()):

    """ Write (debug) info text to stderr.

        extra_lines are shown under the info text.

    """
    info_text = ("""\
### PyRun Debug Information

# Name and version
pyrun_name = %(pyrun_name)r
pyrun_version = %(pyrun_version)r
pyrun_libversion = %(pyrun_libversion)r
pyrun_release = %(pyrun_release)r
pyrun_build = %(pyrun_build)r

# Files and directories
pyrun_executable = %(pyrun_executable)r
pyrun_argv = %(pyrun_argv)r
pyrun_dir = %(pyrun_dir)r
pyrun_binary = %(pyrun_binary)r
pyrun_prefix = %(pyrun_prefix)r
pyrun_bindir = %(pyrun_bindir)r

# Options
pyrun_verbose = %(pyrun_verbose)r
pyrun_debug = %(pyrun_debug)r
pyrun_as_module = %(pyrun_as_module)r
pyrun_as_string = %(pyrun_as_string)r
pyrun_bytecode = %(pyrun_bytecode)r
pyrun_ignore_environment = %(pyrun_ignore_environment)r
pyrun_ignore_pth_files = %(pyrun_ignore_pth_files)r
pyrun_inspect = %(pyrun_inspect)r
pyrun_unbuffered = %(pyrun_unbuffered)r
pyrun_optimized = %(pyrun_optimized)r
pyrun_dontwritebytecode = %(pyrun_dontwritebytecode)r
pyrun_safe_path = %(pyrun_safe_path)r

""" % globals()).splitlines()
    if extra_lines:
        info_text.extend(extra_lines)
    for line in info_text:
        sys.stderr.write('%s\n' % line)

def pyrun_log(line):

    """ Log a line to stderr.

    """
    sys.stderr.write('%s: %s\n' % (pyrun_name, line))

def pyrun_log_error(line):

    """ Log an error line to stderr.

    """
    sys.stderr.write('%s error: %s\n' % (pyrun_name, line))

def pyrun_log_warning(line):

    """ Log a warning line to stderr.

    """
    sys.stderr.write('%s warning: %s\n' % (pyrun_name, line))

def pyrun_parse_cmdline():

    """ Parse the pyrun command line arguments.

        Sets the various options exposed as globals and corrects
        sys.argv after successfully parsing the pyrun options.

    """
    import getopt

    # Parse sys.argv
    valid_options = 'vVmcbiESdOu3h?sBPRIW:X:'
    try:
        parsed_options, remaining_argv = getopt.getopt(pyrun_argv[1:],
                                                       valid_options)
    except getopt.GetoptError as reason:
        pyrun_help(['*** Problem parsing command line: %s' % reason])
        sys.exit(1)

    # Process options
    i = 1
    for arg, value in parsed_options:

        if arg == '-v':
            # Run in verbose mode
            global pyrun_verbose
            pyrun_verbose += 1

        elif arg == '-m':
            # Run script as module
            global pyrun_as_module
            pyrun_as_module = True
            if not remaining_argv:
                pyrun_log_error(
                    'Missing argument for -m. Try pyrun -h for help.')
                sys.exit(1)
            # The remaining arguments may be parsed by the module.
            # -m terminates the option list, just like for Python
            break

        elif arg == '-c':
            # Run argument as command string
            global pyrun_as_string
            pyrun_as_string = True
            if not remaining_argv:
                pyrun_log_error(
                    'Missing argument for -c. Try pyrun -h for help.')
                sys.exit(1)
            # -c terminates the option list, just like for Python
            break

        elif arg == '-b':
            # Run script as bytecode
            global pyrun_bytecode
            pyrun_bytecode = True

        elif arg == '-i':
            # Enable interactive mode
            global pyrun_inspect
            pyrun_inspect = True

        elif arg == '-E':
            # Ignore environment variable settings
            global pyrun_ignore_environment
            pyrun_ignore_environment = True

        elif arg == '-S':
            # Ignore site.py; XXX This is not a true emulation, just
            # an approximation, since it only ignores .pth files, but
            # still applies the rest of the site.py processing
            global pyrun_ignore_pth_files, pyrun_skip_site_main
            pyrun_ignore_pth_files = True
            pyrun_skip_site_main = True

        elif arg == '-d':
            # Show debug info
            global pyrun_debug
            pyrun_debug += 1

        elif arg == '-u':
            # Set stdout and stderr to unbuffered
            global pyrun_unbuffered
            pyrun_unbuffered = True

        elif arg == '-V':
            # Show version and exit
            sys.stdout.write('eGenix PyRun %s (release %s)\n' % (
                pyrun_version,
                pyrun_release))
            sys.exit(0)

        elif arg == '-O':
            # Enable optimization
            global pyrun_optimized
            pyrun_optimized += 1

        elif arg == '-B':
            # Disable writing byte code files
            global pyrun_dontwritebytecode
            pyrun_dontwritebytecode = True

        elif arg == '-R':
            # Enable hash randomization; this doesn't work in PyRun
            # due to the way the randomization is initialized in
            # pythonrun.c
            rc = 1
            pyrun_log_error(
                'Command line option -R is not supported. '
                'Please use PYTHONHASHSEED to enable hash randomization.')
            sys.exit(rc)

        elif arg == '-s':
            # Disable running user site.py
            global pyrun_skip_site_user_site
            pyrun_skip_site_user_site = True

        elif arg == '-P':
            # Disable adding the script or current dir to sys.path
            global pyrun_safe_path
            pyrun_safe_path = True

        elif arg == '-I':
            # Isolate Python from user environment. We implement this as
            # a combination of -E and -s, since PyRun already isolates
            # itself from the user environment in several ways.
            # -E flag: ignore environment
            pyrun_ignore_environment = True
            # -s flag: ignore user site dir
            pyrun_skip_site_user_site = True

        elif arg == '-W':
            # Warning control
            sys.warnoptions.append(value)
            if 'warnings' in sys.modules:
                # If the warnings module was already loaded, the filters
                # will already have been parsed, so we explicitly add
                # the filter here to make sure it gets registered.
                import warnings
                warnings._setoption(value)

        elif arg == '-X':
            # Implementation specific options: not implemented
            if pyrun_debug:
                pyrun_log_warning(
                    'Command line option -X is not supported. '
                    'Ignoring the option.')

        # XXX Add more standard Python command line options here

        # Note: There's a general problem with some options, since by
        # the time the frozen interpreter gets to this code, many
        # options would normally already have had some effect. We'd
        # have to implement the command line parsing in C to fully
        # support the options.
        #
        # The following options are simply ignored for this reason:
        #
        elif arg in ('-3',
                     ):
            # Ignored option, only here for compatibility with
            # standard Python
            pass

        else:
            # Show help
            if arg in ('-h', '-?'):
                extra_lines = []
                rc = 0
            else:
                extra_lines = ['*** Error: Unknown option %r' % arg]
                rc = 1
            pyrun_help(extra_lines)
            sys.exit(rc)

        i += 1

    # Update Python flags, if needed
    if pyrun_optimized:
        sys._setflag('optimize', pyrun_optimized)
    if pyrun_verbose:
        sys._setflag('verbose', pyrun_verbose)
    if pyrun_debug:
        sys._setflag('debug', pyrun_debug)
    if pyrun_inspect:
        sys._setflag('inspect', pyrun_inspect)
    if pyrun_safe_path and sys.version_info[:2] >= (3, 11):
        # config var is only available in Python 3.11+
        sys._setflag('safe_path', pyrun_safe_path)
    if pyrun_dontwritebytecode:
        sys._setflag('dont_write_bytecode', pyrun_dontwritebytecode)
        sys.dont_write_bytecode = pyrun_dontwritebytecode

    # Remove pyrun options from sys.argv
    sys.argv[:] = remaining_argv

def pyrun_normpath(path,

                   _home_env='HOME',
                   _home_prefix='~' + os.sep):

    """ Normalize path to make it absolute and also do
        limited tilde expansion (for the home dir).

    """
    path = path.strip()

    # Apply limited tilde expansion
    if path == '~':
        path = os.environ.get(_home_env, '~')

    elif path[:2] == _home_prefix:
        home = os.environ.get(_home_env, None)
        if home is not None:
            if home.endswith(os.sep):
                path = home + path[2:]
            else:
                path = home + os.sep + path[2:]

    # Convert to an absolute path
    return os.path.abspath(path)

def pyrun_prompt(pyrun_script='<stdin>', banner=None):

    """ Start an interactive pyrun prompt for pyrun_script.

        banner is used as startup text. It defaults to pyrun_banner().

    """
    import code

    # Try to import readline for better keyboard support
    try:
        import readline
    except ImportError:
        pass

    # Defaults
    if banner is None:
        banner = pyrun_banner()

    # Setup globals and run interpreter interactively
    runtime_globals = globals()
    runtime_globals.update(__name__='__main__',
                           __file__=pyrun_script)
    if sys.version_info < (3, 6):
        code.interact(banner, raw_input, runtime_globals)
    else:
        # Python 3.6 introduce an exit message and comes with
        # an annoying default value which we'll supress here
        code.interact(banner, raw_input, runtime_globals,
                      exitmsg='')

def pyrun_enable_unbuffered_mode():

    """ Enable unbuffered sys.stdout/stderr.

    """
    if pyrun_debug > 1:
        pyrun_log('Enabling unbuffered mode')

    # Reopen in write binary unbuffered mode
    stdout = os.fdopen(sys.stdout.fileno(), 'wb', 0)
    stderr = os.fdopen(sys.stderr.fileno(), 'wb', 0)

    # Assign new file objects
    if PY3:
        # For Python 3, wrap the streams into TextIOWrapper
        import io
        sys.stdout = io.TextIOWrapper(stdout,
                                      encoding=sys.stdout.encoding,
                                      errors=sys.stdout.errors,
                                      write_through=True)
        sys.stderr = io.TextIOWrapper(stderr,
                                      encoding=sys.stderr.encoding,
                                      errors=sys.stderr.errors,
                                      write_through=True)
    else:
        # Python 2
        sys.stdout = stdout
        sys.stderr = stderr

def pyrun_run_site_main():

    """ Import the site module

    """
    if pyrun_debug > 1:
        pyrun_log('Importing site.py')
        pyrun_log('  sys.path before importing site:')
        for path in sys.path:
            pyrun_log('    %s' % path)
    import site
    site.PREFIXES = [sys.prefix]
    if pyrun_skip_user_site:
        site.ENABLE_USER_SITE = False
    site.main()
    if pyrun_debug > 1:
        pyrun_log('  sys.path after importing site:')
        for path in sys.path:
            pyrun_log('    %s' % path)

def pyrun_setup_sys_path(pyrun_script=None):

    """ Setup the sys.path in preparation for running pyrun_script.

        pyrun_script may be None in case the script file name is not
        available (e.g. when starting interactive mode or running code
        compiled from the command line parameters).

    """
    exists = os.path.exists
    join = os.path.join
    if pyrun_debug > 1:
        pyrun_log('Setting up sys.path')
        pyrun_log('  sys.path before adjusting it (compile time version):')
        for path in sys.path:
            pyrun_log('    %s' % path)

    # Determine various default locations
    if pyrun_script is not None:
        # Use the script dir as first sys.path dir
        pyrun_script = pyrun_normpath(pyrun_script)
        pyrun_script_dir = os.path.split(pyrun_script)[0]
    else:
        # Use the current directory as first sys.path dir
        pyrun_script_dir = os.getcwd()
    pyrun_script_dir = pyrun_normpath(pyrun_script_dir)
    python_lib = join(pyrun_prefix, 'lib', 'python' + pyrun_libversion)
    if not exists(python_lib):
        python_lib = join(pyrun_dir, 'lib', 'python' + pyrun_libversion)
    python_lib = pyrun_normpath(python_lib)
    python_lib_dynload = join(python_lib, 'lib-dynload')
    python_site_package = join(python_lib, 'site-packages')
    # all path variables should be normalized now

    # Build sys.path
    if not pyrun_safe_path:
        # start with the script directory (location of the script to be
        # run)
        sys.path = [pyrun_script_dir]
    else:
        sys.path = []

    # Add PYTHONPATH; note: these are not processed for .pth files
    if not pyrun_ignore_environment:
        pythonpath = os.environ.get('PYTHONPATH', None)
        if pythonpath is not None:
            sys.path.extend([
                pyrun_normpath(path)
                for path in pythonpath.split(os.pathsep)])

    # Add python_lib and python_lib_dynload (location of additional
    # pyrun shared modules)
    sys.path.append(python_lib)
    sys.path.append(python_lib_dynload)

    # Add site packages directory
    if pyrun_ignore_pth_files:
        # Add the standard dirs without any .pth processing
        sys.path.append(python_site_package)
    else:
        # Use site.addsitedir() to add site-package dirs with
        # .pth processing (needed for setuptools/pip et al.)
        import site
        known_paths = site.addsitedir(python_site_package)
        #site.addsitedir(another_site_package, known_paths)

    if pyrun_debug > 1:
        pyrun_log('  sys.path after adjusting it (before cleanup):')
        for path in sys.path:
            pyrun_log('    %s' % path)

    # Finally, remove non-existing entries
    exists = os.path.exists
    sys.path = [dir
                for dir in sys.path
                if exists(dir)]

    if pyrun_debug > 1:
        pyrun_log('  sys.path final version:')
        for path in sys.path:
            pyrun_log('    %s' % path)

def pyrun_execute_script(pyrun_script, mode='file'):

    """ Run pyrun_script with pyrun.

        pyrun_script may point to a Python script file, Python
        bytecode file or a module name, depending on mode:

        mode defines the run method:

        'file'       - run as Python source file (default)
        'path'       - run as Python path, i.e. directory or
                       ZIP file with __main__ module (Python 2.7 only)
        'module'     - lookup as module on sys.path and run as module
        'codefile'   - run as .pyc file (default, if pyrun_script ends
                       with .pyc or .pyo)
        'string'     - run as Python source string
        'codestring' - run as Python byte code string (in .pyc format)

    """
    # Run the pyrun_script
    if pyrun_debug > 1:
        pyrun_log('Executing script %r in mode %r' % (
            pyrun_script, mode))
        pyrun_log('  sys.argv=%r' % sys.argv)
        pyrun_log('  sys.path=%r' % sys.path)
        pyrun_log('  globals()=%r' % globals())

    # Adjust defaults
    if (mode == 'file' and
        (pyrun_script.endswith('.pyc') or
         pyrun_script.endswith('.pyo'))):
        mode = 'codefile'

    if mode == 'module':

        ### Run pyrun_script as module (much like python -m <module>)

        if pyrun_verbose:
            pyrun_log('Running %r as module' % pyrun_script)
        # sys.argv[0]: runpy will set the sys.argv[0] to the absolute
        # location of the found module
        import runpy
        try:
            runpy.run_module(pyrun_script, globals(), '__main__', True)
        except ImportError as reason:
            pyrun_log_error('Could not run %r: %s' % (pyrun_script, reason))
            sys.exit(1)

    elif mode == 'path':

        ### Run pyrun_script as path (much like python <path>)
        #
        # Only supported in Python 2.7+. Can handle .py files, ZIP
        # files and directories with __main__.py module.
        #

        if pyrun_verbose:
            pyrun_log('Running %r as path' % pyrun_script)

        # About sys.argv[0]:
        #
        # runpy.run_path() will setup sys.argv[0] in the following
        # way:
        #
        # * if pyrun_script points to a directory with __main__.py
        #   module, to the directory containing __main__.py
        #
        # * if pyrun_script points to a ZIP file, to the name of
        #   the zip file
        #
        # * in case pyrun_script points to a .py file in some subdir,
        #   to the current directory
        #
        #   WARNING: This is different than standard Python, which
        #   places the directory of the .py file in sys.argv[0].
        #
        import runpy
        try:
            runpy.run_path(pyrun_script, globals(), '__main__')
        except ImportError as reason:
            pyrun_log_error('Could not run %r: %s' % (pyrun_script, reason))
            sys.exit(1)
        except (ValueError, TypeError) as reason:
            # Unfortunately, trying to import a non-ZIP file as
            # package will result in a ValueError (in Python 3) or
            # TypeError (in Python 2) rather than an ImportError. We
            # do some extra checks here to prevent masking application
            # level ValueErrors.
            reason = str(reason)
            if ('string without null bytes' not in reason and
                'source code string' not in reason):
                raise
            if pyrun_mode == 'app':
                # For app mode, change the reason to something more
                # useful
                reason = 'app missing appended ZIP package'
            pyrun_log_error('Could not run %r: %s' % (pyrun_script, reason))
            sys.exit(1)

    elif (mode == 'codefile' or mode == 'codestring'):

        ### Run pyrun_script as bytecode file or string

        import marshal
        if PY3:
            # Python 3
            import importlib.util
            MAGIC = importlib.util.MAGIC_NUMBER
        else:
            # Python 2
            import imp
            MAGIC = imp.get_magic()

        if mode == 'codefile':
            if pyrun_verbose:
                pyrun_log('Running %r as bytecode file' % pyrun_script)
            if not os.access(pyrun_script, os.R_OK):
                pyrun_log_error('Could not find/read script file %r' %
                                pyrun_script)
                sys.exit(1)
            # sys.argv[0]: should be the same as pyrun_script
            assert sys.argv[0] == pyrun_script
            module_file = open(pyrun_script, 'rb')

        elif mode == 'codestring':
            if pyrun_verbose:
                pyrun_log('Running pyrun_script as bytecode string')
            # sys.argv[0]: We mimic Python when using the -c option
            sys.argv[0] = '-c'
            import cStringIO
            module_file = cStringIO.StringIO(pyrun_script)

        # Check magic
        if module_file.read(4) != MAGIC:
            pyrun_log_error('Incompatible bytecode file %r' % pyrun_script)
            sys.exit(1)

        # Skip timestamp (32 bits)
        module_file.read(4)

        # Load code object
        module_code = marshal.load(module_file)

        # Close file
        module_file.close()

        # Exec code in globals
        runtime_globals = globals()
        runtime_globals.update(__name__='__main__',
                               __file__=pyrun_script)
        pyrun_exec_code(module_code, runtime_globals)

    elif mode == 'file':

        ### Run pyrun_script as .py file

        if pyrun_verbose:
            pyrun_log('Running %r as script' % pyrun_script)
        if not os.access(pyrun_script, os.R_OK):
            pyrun_log_error('Could not find/read script file %r' %
                            pyrun_script)
            sys.exit(1)

        # sys.argv[0]: should be the same as pyrun_script
        assert sys.argv[0] == pyrun_script

        # Exec script file in globals
        runtime_globals = globals()
        runtime_globals.update(__name__='__main__',
                               __file__=pyrun_script)
        pyrun_exec_code_file(pyrun_script, runtime_globals, runtime_globals)

    elif mode == 'string':

        ### Run pyrun_script as source string

        if pyrun_verbose:
            pyrun_log('Running pyrun_script as string')

        # Compile string into code object
        script_path = '<stdin>'
        if not pyrun_script.endswith('\n'):
            # No longer needed in Python 2.7, but better safe than
            # sorry
            pyrun_script += '\n'
        code = compile(pyrun_script, script_path, 'exec')

        # sys.argv[0]: We mimic Python when using the -c option
        sys.argv[0] = '-c'

        # Exec code in globals
        runtime_globals = globals()
        runtime_globals.update(__name__='__main__',
                               __file__=script_path)
        pyrun_exec_code(code, runtime_globals)

    else:
        raise TypeError('unknown execution mode %r' % mode)

### Main entry point

def pyrun_main():

    global pyrun_mode, pyrun_app, pyrun_as_string, \
           pyrun_as_module, pyrun_script

    # Determine run mode
    pyrun_mode = 'script'
    pyrun_app = os.path.split(sys.executable)[1]
    if not pyrun_app.startswith(('pyrun', 'python')):
        # Renaming the pyrun executable triggers app mode
        pyrun_mode = 'app'

    # Parse the command line and get the script name (if not in app
    # mode)
    if pyrun_mode != 'app':
        pyrun_parse_cmdline()

        # Check for interactive mode, now that we have the command
        # line parsed
        if not sys.argv and sys.stdin.isatty():
            pyrun_mode = 'interactive'

    # Enable unbuffered mode
    if pyrun_unbuffered:
        pyrun_enable_unbuffered_mode()

    # Update run-time environment
    pyrun_update_runtime()

    # Show debug info
    if pyrun_debug:
        pyrun_info()

    # Start the runtime in various modes

    if pyrun_mode == 'script':

        ### Run a script

        # Setup script to run
        if not sys.argv:
            # Filter mode: read the script from stdin
            if pyrun_as_string or pyrun_as_module:
                # Missing script argument
                pyrun_log_error(
                    'Missing argument for -c/-m. Try pyrun -h for help.')
                sys.exit(1)
            else:
                pyrun_as_string = True
            pyrun_script = sys.stdin.read()
            sys.argv = ['']

        elif sys.argv[0] == '-' and not (pyrun_as_string or pyrun_as_module):
            # Read the script from stdin
            pyrun_as_string = True
            pyrun_script = sys.stdin.read()

        else:
            # Default operation: run the script given as first
            # argument
            pyrun_script = sys.argv[0]

        # Setup paths & mode
        script_path = pyrun_script
        if pyrun_as_module:
            script_mode = 'module'
            script_path = None
        elif pyrun_as_string:
            script_mode = 'string'
            script_path = None
        else:
            if pyrun_version < '2.7.0':
                script_mode = 'file'
            # Python 2.7 and later
            elif (pyrun_script.endswith('.py') or
                  pyrun_script.endswith('.pyw')):
                script_mode = 'file'
            else:
                # Use path mode for all other files, since this
                # provides support for directories, ZIP files, etc.
                script_mode = 'path'

        # Setup sys.path
        pyrun_setup_sys_path(script_path)

        # Import site module and run site.main() (which is not run by
        # pyrun per default like in standard Python; see makepyrun.py)
        if not pyrun_skip_site_main:
            pyrun_run_site_main()

        # Run the script
        try:
            pyrun_execute_script(pyrun_script, script_mode)
        except Exception as reason:
            if pyrun_inspect:
                import traceback
                traceback.print_exc()
                pyrun_prompt(banner='')
            else:
                raise
        else:
            # Enter interactive mode, in case wanted
            if pyrun_inspect:
                pyrun_prompt()

        # Exit
        sys.exit(0)

    elif pyrun_mode == 'app':

        ### App mode: run the executable itself via package import

        # Run the executable as ZIP Python package (imports top-level
        # __main__ module from the appended ZIP file and runs it)
        pyrun_script = sys.executable

        # Setup sys.path
        pyrun_setup_sys_path(pyrun_script)

        # Import site module and run site.main() (which is not run by
        # pyrun per default like in standard Python; see makepyrun.py)
        if not pyrun_skip_site_main:
            pyrun_run_site_main()

        # Run the script
        try:
            pyrun_execute_script(pyrun_script, 'path')
        except Exception as reason:
            if pyrun_inspect:
                import traceback
                traceback.print_exc()
                pyrun_prompt(banner='')
            else:
                raise
        else:
            # Enter interactive mode, in case wanted
            if pyrun_inspect:
                pyrun_prompt()

        # Exit
        sys.exit(0)

    elif pyrun_mode == 'interactive':

        ### Enter interactive mode

        # Setup sys.path
        pyrun_setup_sys_path()

        # Import site module and run site.main() (which is not run by
        # pyrun per default like in standard Python; see makepyrun.py)
        if not pyrun_skip_site_main:
            pyrun_run_site_main()

        # Setup sys.argv for interactive mode
        if not sys.argv:
            sys.argv = ['']

        # Enter interactive mode
        pyrun_prompt()

        # Disable inspect mode to not enter a prompt after the
        # following sys.exit()
        if pyrun_inspect:
            sys._setflag('inspect', 0)

        # Exit
        sys.exit(0)

    else:
        raise TypeError('Unsupported pyrun execution mode: %r' % pyrun_mode)
