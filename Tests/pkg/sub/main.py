print "__file__: %r" % __file__
print "__name__: %r" % __name__
try:
    print "__path__: %r" % __path__
except NameError:
    print "__path__: not defined"
import sys
print "sys.path[0]: %r" % sys.path[0]
