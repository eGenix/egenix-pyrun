#!/usr/bin/env python
#
# Test the pyrun cmd line interface.
#
# Note: This test currently only works on Unix platforms and then only
#       for Python 2.7. See #1076.
#
import os, sys, subprocess, re

PYRUN = 'pyrun'
PYTHON = 'python2.7'
TESTDIR = os.path.abspath('Tests')

def run(command):

    pipe = subprocess.Popen(command, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return pipe.stdout.read() + pipe.stderr.read()

def python_version(runtime):

    return run('%s "import sys; sys.version.split()[0]"' %
               runtime).strip()

def match_result(result, pattern):

    m = re.match(pattern.replace('[0]', '\[0\]'), result)
    if m is None:
        print ('*** Result  %r does not match\n'
               '    pattern %r' % (result, pattern))
    return m

def test_cmd_line(runtime=PYRUN):

    os.chdir(TESTDIR)

    l = []
    result = run('%s hello.py' % runtime)
    assert match_result(
        result,
        'Hello world !\n'
        )
    l.append(result)
    
    result = run('%s main.py' % runtime)
    assert match_result(
        result,
        "__file__: 'main.py'\n"
        "__name__: '__main__'\n"
        "__path__: not defined\n"
        "sys.path[0]: '%s'\n" % os.path.abspath(os.getcwd())
        )
    l.append(result)
    
    result = run('%s pkg/main.py' % runtime)
    assert match_result(
        result,
        "__file__: 'pkg/main.py'\n"
        "__name__: '__main__'\n"
        "__path__: not defined\n"
        "sys.path[0]: '.*/pkg'\n"
        )
    l.append(result)

    result = run('%s pkg/sub/main.py' % runtime)
    assert match_result(
        result,
        "__file__: 'pkg/sub/main.py'\n"
        "__name__: '__main__'\n"
        "__path__: not defined\n"
        "sys.path[0]: '.*/pkg/sub'\n"
        )
    l.append(result)
    
    # These features are only supported in pyrun 2.7
    if python_version(runtime) >= '2.7':
        result = run('%s dir' % runtime)
        assert match_result(
            result,
            "__file__: '.*/dir/__main__.py'\n"
            "__name__: '__main__'\n"
            "__path__: not defined\n"
            "sys.path[0]: 'dir'\n"
            )
        l.append(result)
    
        result = run('%s zipfiles.zip' % runtime)
        assert match_result(
            result,
            "__file__: 'zipfiles.zip/__main__.py'\n"
            "__name__: '__main__'\n"
            "__path__: not defined\n"
            "sys.path[0]: 'zipfiles.zip'\n"
            )
        l.append(result)
    
        result = run('%s zipfiles.abc' % runtime)
        assert match_result(
            result,
            "__file__: 'zipfiles.abc/__main__.py'\n"
            "__name__: '__main__'\n"
            "__path__: not defined\n"
            "sys.path[0]: 'zipfiles.abc'\n"
            )
        l.append(result)

        result = run('%s zipdir.zip' % runtime)
        assert match_result(
            result,
            ".*: can't find ('__main__' module|'__main__.py') in 'zipdir.zip'\n"
            )
        l.append(result)

    return l

def test_O_flag(runtime=PYRUN):

    os.chdir(TESTDIR)

    result = run('%s -c "assert 1==1; print (\'ok\')"' % runtime)
    assert match_result(
        result,
        "ok\n"
        )
    
    result = run('%s -c "assert 1==0; print (\'ok\')"' % runtime)
    assert match_result(
        result,
        "(?s).*AssertionError.*"
        )
    
    result = run('%s -O -c "assert 1==1; print (\'ok\')"' % runtime)
    assert match_result(
        result,
        "ok\n"
        )
    
    result = run('%s -O -c "assert 1==0; print (\'ok\')"' % runtime)
    assert match_result(
        result,
        "ok\n"
        )
    
    result = run('%s -O -c "import sys; print (sys._setflag(\'optimize\'))"' %
                 runtime)
    assert match_result(
        result,
        "1\n"
        )
    
    result = run('%s -OO -c "import sys; print (sys._setflag(\'optimize\'))"' %
                 runtime)
    assert match_result(
        result,
        "2\n"
        )
    
def test_d_flag(runtime=PYRUN):

    os.chdir(TESTDIR)

    result = run('%s -c "print (\'ok\')"' % runtime)
    assert match_result(
        result,
        "ok\n"
        )
    
    result = run('%s -d -c "import sys; print (sys._setflag(\'debug\'))"' %
                 runtime)
    assert match_result(
        result,
        "1\n"
        )
    
    result = run('%s -dd -c "import sys; print (sys._setflag(\'debug\'))"' %
                 runtime)
    assert match_result(
        result,
        "2\n"
        )
    
###

if __name__ == '__main__':
    try:
        runtime = sys.argv[1]
    except IndexError:
        print '%s <abs path to runtime>' % sys.argv[0]
        sys.exit(1)
    test_cmd_line(runtime)
    test_O_flag(runtime)
    test_d_flag(runtime)
    print '%s passes all command line tests' % runtime
