import marshal
import bkfile


# Write a file containing frozen code for the modules in the dictionary.

header = """
#include "Python.h"

static struct _frozen _PyImport_FrozenModules[] = {
"""
trailer = """\
    {0, 0, 0} /* sentinel */
};
"""

default_entry_point = """

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

def makefreeze(base, dict, debug=0, entry_point=None, fail_import=()):
    if entry_point is None: entry_point = default_entry_point
    done = []
    files = []
    mods = dict.keys()
    mods.sort()
    for mod in mods:
        m = dict[mod]
        mangled = "__".join(mod.split("."))
        if m.__code__:
            file = 'M_' + mangled + '.c'
            outfp = bkfile.open(base + file, 'w')
            files.append(file)
            if debug:
                print "freezing", mod, "..."
            str = marshal.dumps(m.__code__)
            size = len(str)
            if m.__path__:
                # Indicate package by negative size
                size = -size
            done.append((mod, mangled, size))
            writecode(outfp, mangled, str)
            outfp.close()
    if debug:
        print "generating table of frozen modules"
    outfp = bkfile.open(base + 'frozen.c', 'w')
    for mod, mangled, size in done:
        outfp.write('extern unsigned char M_%s[];\n' % mangled)
    outfp.write(header)
    for mod, mangled, size in done:
        outfp.write('\t{"%s", M_%s, %d},\n' % (mod, mangled, size))
    outfp.write('\n')
    # The following modules have a NULL code pointer, indicating
    # that the prozen program should not search for them on the host
    # system. Importing them will *always* raise an ImportError.
    # The zero value size is never used.
    for mod in fail_import:
        outfp.write('\t{"%s", NULL, 0},\n' % (mod,))
    outfp.write(trailer)
    outfp.write(entry_point)
    outfp.close()
    return files



# Write a C initializer for a module containing the frozen python code.
# The array is called M_<mod>.

def writecode(outfp, mod, str):
    outfp.write('unsigned char M_%s[] = {' % mod)
    for i in range(0, len(str), 16):
        outfp.write('\n\t')
        for c in str[i:i+16]:
            outfp.write('%d,' % ord(c))
    outfp.write('\n};\n')

## def writecode(outfp, mod, str):
##     outfp.write('unsigned char M_%s[%d] = "%s";\n' % (mod, len(str),
##     '\\"'.join(map(lambda s: repr(s)[1:-1], str.split('"')))))
