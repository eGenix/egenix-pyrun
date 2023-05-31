import sys
print ('stdin.encoding = %r, .errors = %r' % (
    sys.stdin.encoding, sys.stdout.errors))
print ('stdout.encoding = %r, .errors = %r' % (
    sys.stdout.encoding, sys.stdout.errors))

data = sys.stdin.read()
print ('Received data: %r' % data)
sys.stdout.write(data)
