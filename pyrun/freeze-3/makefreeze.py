import marshal
import bkfile
import sys

# The frozen array struct changed in 3.11
PY311GE = (sys.version_info[:2] >= (3, 11))

# Write a file containing frozen code for the modules in the dictionary.

header = """
#include "Python.h"

static struct _frozen _PyImport_FrozenModules[] = {
"""
trailer = """\
    {0, 0, 0} /* sentinel */
};
"""

# This version does not work in Python 3.7, since the libpython already
# includes a Py_GetArgcArgv() function.
old_default_entry_point = """

/* For Py_GetArgcArgv(); set by main() */
static char **orig_argv;
static int  orig_argc;

/* Make the *original* argc/argv available to other modules.
   This is rare, but it is needed by the secureware extension. */

void
Py_GetArgcArgv(int *argc, char ***argv)
{
    *argc = orig_argc;
    *argv = orig_argv;
}

int
main(int argc, char **argv)
{
        extern int Py_FrozenMain(int, char **);

        /* Disabled, since we want to default to non-optimized mode: */
        /* Py_OptimizeFlag++; */
        Py_NoSiteFlag++;        /* Don't import site.py */
        orig_argc = argc;	/* For Py_GetArgcArgv() */
        orig_argv = argv;

        PyImport_FrozenModules = _PyImport_FrozenModules;
        return Py_FrozenMain(argc, argv);
}

"""

default_entry_point = """

int
main(int argc, char **argv)
{
        extern int Py_FrozenMain(int, char **);

        /* Disabled, since we want to default to non-optimized mode: */
        /* Py_OptimizeFlag++; */
        Py_NoSiteFlag++;        /* Don't import site.py */

        PyImport_FrozenModules = _PyImport_FrozenModules;
        return Py_FrozenMain(argc, argv);
}

"""

def makefreeze(base, dict, debug=0, entry_point=None, fail_import=()):
    if entry_point is None: entry_point = default_entry_point
    done = []
    files = []
    mods = sorted(dict.keys())
    for mod in mods:
        m = dict[mod]
        mangled = "__".join(mod.split("."))
        if m.__code__:
            file = '_Py_M_' + mangled + '.c'
            with bkfile.open(base + file, 'w') as outfp:
                files.append(file)
                if debug:
                    print("freezing", mod, "...")
                str = marshal.dumps(m.__code__)
                size = len(str)
                if m.__path__:
                    # Indicate package by negative size
                    size = -size
                done.append((mod, mangled, size))
                writecode(outfp, mangled, str)
    if debug:
        print("generating table of frozen modules")
    with bkfile.open(base + 'frozen.c', 'w') as outfp:
        for mod, mangled, size in done:
            outfp.write('extern const unsigned char _Py_M_%s[];\n' % mangled)
        outfp.write(header)
        for mod, mangled, size in done:
            if PY311GE:
                # New 3.11 format for packages
                if size < 0:
                    size = -size
                    is_package = 1
                else:
                    is_package = 0
                outfp.write('\t{"%s", _Py_M_%s, %d, %d},\n' % (mod, mangled, size, is_package))
            else:
                # Old format
                outfp.write('\t{"%s", _Py_M_%s, %d},\n' % (mod, mangled, size))
        outfp.write('\n')
        # The following modules have a NULL code pointer, indicating
        # that the frozen program should not search for them on the host
        # system. Importing them will *always* raise an ImportError.
        # The zero value size is never used.
        for mod in fail_import:
            outfp.write('\t{"%s", NULL, 0},\n' % (mod,))
        outfp.write(trailer)
        outfp.write(entry_point)
    return files



# Write a C initializer for a module containing the frozen python code.
# The array is called _Py_M_<mod>.

def writecode(fp, mod, data):
    print('const unsigned char _Py_M_%s[] = {' % mod, file=fp)
    indent = ' ' * 4
    for i in range(0, len(data), 16):
        print(indent, file=fp, end='')
        for c in bytes(data[i:i+16]):
            print('%d,' % c, file=fp, end='')
        print('', file=fp)
    print('};', file=fp)
