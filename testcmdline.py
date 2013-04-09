#!/usr/bin/env python
#
# Test the pyrun cmd line interface
#
import os, sys, subprocess

PYRUN = 'pyrun'
PYTHON = 'python2.7'
TESTDIR = 'Tests'

def run(command):

    pipe = subprocess.Popen(command, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    return pipe.stdout.read() + pipe.stderr.read()

def test_cmd_line(runtime=PYRUN):

    os.chdir(TESTDIR)

    result = run('%s hello.py' % runtime)
    print repr(result)
    assert result == 'Hello world !\n'
    
    result = run('%s main.py' % runtime)
    print repr(result)
    #assert result == 'Hello world !\n'
    
    result = run('%s pkg/main.py' % runtime)
    print repr(result)

    result = run('%s pkg/sub/main.py' % runtime)
    print repr(result)
    
    result = run('%s dir' % runtime)
    print repr(result)
    
    result = run('%s zipfiles.zip' % runtime)
    print repr(result)
    
    result = run('%s zipfiles.abc' % runtime)
    print repr(result)
    
    result = run('%s zipdir.zip' % runtime)
    print repr(result)
    
###

if __name__ == '__main__':
    test_cmd_line(sys.argv[1])
