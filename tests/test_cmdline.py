#!/usr/bin/env python
#
# Test the pyrun cmd line interface.
#
# Note: This test currently only works on Unix platforms.
#

import os, sys, subprocess, re, shutil

PYRUN = 'pyrun'
PYTHON = 'python2.7'
TESTDIR = os.path.abspath('tests')

# Enable debug output ?
_debug = 0

# Double check that asserts work
try:
    assert False
except AssertionError:
    pass
else:
    raise RuntimeError('asserts are disabled - cannot run tests')

def run(command, encoding='utf-8'):

    if _debug:
        print ('Running %s' % command)
    pipe = subprocess.Popen(command, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout_data, stderr_data = pipe.communicate()
    result = stdout_data + stderr_data
    return result.decode(encoding)

def python_version(runtime):

    return run('%s '
               '-c "import sys; sys.stdout.write(sys.version.split()[0])"' %
               runtime).strip()

def match_result(result, pattern):

    m = re.match(pattern.replace('[0]', '\[0\]'), result, re.MULTILINE)
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

    result = run('%s -S main.py' % runtime)
    assert match_result(
        result,
        "__file__: 'main.py'\n"
        "__name__: '__main__'\n"
        "__path__: not defined\n"
        "sys.path[0]: '%s'\n" % os.path.abspath(os.getcwd())
        )
    l.append(result)

    result = run('%s -S pkg/main.py' % runtime)
    assert match_result(
        result,
        "__file__: 'pkg/main.py'\n"
        "__name__: '__main__'\n"
        "__path__: not defined\n"
        "sys.path[0]: '.*/pkg'\n"
        )
    l.append(result)

    result = run('%s -S pkg/sub/main.py' % runtime)
    assert match_result(
        result,
        "__file__: 'pkg/sub/main.py'\n"
        "__name__: '__main__'\n"
        "__path__: not defined\n"
        "sys.path[0]: '.*/pkg/sub'\n"
        )
    l.append(result)

    # These features are only supported in pyrun 2.7 and 3.4+.
    if python_version(runtime) >= '2.7':
        result = run('%s -S dir' % runtime)
        assert match_result(
            result,
            # XXX Note: In Python 3.4, the __file__ attribute for
            #     dir imports is relative, not absolute as for
            #     Python 2.7. Not sure whether this is a bug in
            #     PyRun or just a different behavior in Python 3.
            "__file__: '.*/?dir/__main__.py'\n"
            "__name__: '__main__'\n"
            "__path__: not defined\n"
            "sys.path[0]: 'dir'\n"
            )
        l.append(result)

        result = run('%s -S zipfiles.zip' % runtime)
        assert match_result(
            result,
            "__file__: 'zipfiles.zip/__main__.py'\n"
            "__name__: '__main__'\n"
            "__path__: not defined\n"
            "sys.path[0]: 'zipfiles.zip'\n"
            )
        l.append(result)

        result = run('%s -S zipfiles.abc' % runtime)
        assert match_result(
            result,
            "__file__: 'zipfiles.abc/__main__.py'\n"
            "__name__: '__main__'\n"
            "__path__: not defined\n"
            "sys.path[0]: 'zipfiles.abc'\n"
            )
        l.append(result)

        result = run('%s -S zipdir.zip' % runtime)
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

    if sys.version.startswith('3.10.0'):
        # Tokenizer in this version has a bug, so the following does not
        # work correctly. See https://bugs.python.org/issue45562
        return

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

def test_v_flag(runtime=PYRUN):

    os.chdir(TESTDIR)

    result = run('%s -c "print (\'ok\')"' % runtime)
    assert match_result(
        result,
        "ok\n"
        )

    result = run('%s -v -c '
                 '"import sys; '
                 'print (\'verbose=%%r\' %% sys._setflag(\'verbose\'))"' %
                 runtime)
    assert match_result(
        result,
        "verbose=1\n(import .*|# zipimport: found .*|# destroy sitecustomize.*)"
        )

    result = run('%s -vv -c '
                 '"import sys; '
                 'print (\'verbose=%%r\' %% sys._setflag(\'verbose\'))"' %
                 runtime)
    assert match_result(
        result,
        "verbose=2\n(import .*|# zipimport: found .*|# destroy sitecustomize.*)"
        )

def test_s_flag(runtime=PYRUN):

    os.chdir(TESTDIR)

    result = run('%s -s -c "print (\'ok\')"' % runtime)
    assert match_result(
        result,
        "ok\n"
        )

def test_B_flag(runtime=PYRUN):

    os.chdir(TESTDIR)

    PYC_FILE = 'testmod.pyc'
    PYC_CACHE = '__pycache__'
    if os.path.exists(PYC_FILE):
        os.remove(PYC_FILE)
    if os.path.exists(PYC_CACHE):
        shutil.rmtree(PYC_CACHE)
    open('testmod.py', 'w').write('print("ok")\n')

    result = run('%s -B -c "import testmod"' % runtime)
    assert match_result(
        result,
        "ok\n"
        )
    assert not os.path.exists(PYC_FILE)
    assert not os.path.exists(PYC_CACHE)

def test_R_flag(runtime=PYRUN):

    os.chdir(TESTDIR)

    if 0:
        # These test would work, but pythonrun.c implements the
        # randomization in a way which doesn't allow PyRun to set the
        # flag (and let it have an effect) after Python
        # initialization.
        result1 = run('%s -c "print (hash("a"))"' % runtime)
        result2 = run('%s -c "print (hash("a"))"' % runtime)
        assert result1 == result2

        result1 = run('%s -R -c "print (hash("a"))"' % runtime)
        result2 = run('%s -R -c "print (hash("a"))"' % runtime)
        assert result1 != result2

    else:
        # Just check for error message
        result = run('%s -R -c "1"' % runtime)
        assert match_result(
            result,
            "(?s).*PYTHONHASHSEED.*"
            )

def test_W_flag(runtime=PYRUN):

    os.chdir(TESTDIR)

    result = run(
        '%s -W ignore '
        '-c "import warnings; warnings.warn(\'test\'); print (\'done\')"' %
        runtime)
    assert 'test' not in result

def test_m_flag(runtime=PYRUN):

    os.chdir(TESTDIR)

    result = run(
        '%s -m showargv' %
        runtime)
    assert 'showargv' in result

    result = run(
        '%s -m showargv -n' %
        runtime)
    assert 'showargv' in result
    assert '-n' in result

def test_c_flag(runtime=PYRUN):

    os.chdir(TESTDIR)

    result = run(
        '%s -c "import sys; print(sys.argv)"' %
        runtime)
    assert '-c' in result

    result = run(
        '%s -c "import sys; print(sys.argv)" -n' %
        runtime)
    assert '-c' in result
    assert '-n' in result

def test_s_flag(runtime=PYRUN):

    os.chdir(TESTDIR)

    result = run(
        '%s -s -c "print (pyrun_skip_site_user_site)"' %
        runtime)
    assert 'True' in result

def test_E_flag(runtime=PYRUN):

    os.chdir(TESTDIR)

    result = run(
        '%s -E -c '
        '"print (pyrun_ignore_environment)"' %
        runtime)
    assert 'True' in result

def test_I_flag(runtime=PYRUN):

    os.chdir(TESTDIR)

    result = run(
        '%s -I -c '
        '"print (pyrun_skip_site_user_site and pyrun_ignore_environment)"' %
        runtime)
    assert 'True' in result

###

if __name__ == '__main__':
    try:
        runtime = sys.argv[1]
    except IndexError:
        runtime = sys.executable
        print('Using %s as runtime.' % runtime)
    print('Testing Python %s command line emulation' % python_version(runtime))
    test_cmd_line(runtime)
    test_O_flag(runtime)
    test_d_flag(runtime)
    test_v_flag(runtime)
    test_s_flag(runtime)
    test_B_flag(runtime)
    test_R_flag(runtime)
    test_W_flag(runtime)
    test_m_flag(runtime)
    test_c_flag(runtime)
    test_E_flag(runtime)
    test_I_flag(runtime)
    test_s_flag(runtime)
    print('%s passes all command line tests' % runtime)
