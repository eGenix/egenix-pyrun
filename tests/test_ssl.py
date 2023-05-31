""" Test SSL and HTTPS connectivity of pyrun.

"""

import sys, os

### Constants

PYTHON_VERSION = sys.version_info
PY3 = (PYTHON_VERSION[0] == 3)

###

# Try to load egenix-pyopenssl (with embedded SSL libs)
if not PY3:
    print ('Trying to use SSL libs from egenix-pyopenssl.')
    try:
        import OpenSSL
    except ImportError:
        print ('Could not find egenix-pyopenssl. Using system SSL libs.')
    except:
        print ('Loaded SSL libs from egenix-pyopenssl.')
else:
    print ('Testing loading of SSL libs...')
    import ssl

if not PY3:
    from urllib import urlopen
else:
    from urllib.request import urlopen


# Try a few URLs (which should all deliver at least 1k data)
chunk = 1024
for url in ('https://www.python.org/',
            'https://pypi.python.org/',
            'https://www.egenix.com/',
            ):
    webpage = urlopen(url)
    data = webpage.read(chunk)
    assert len(data) == chunk, 'URL %s did not return enough data' % url
    webpage.close()

# Try URLs which are not using a trusted certificate
chunk = 100
failures = 0
for url in ('https://self-signed.badssl.com/',
            'https://untrusted-root.badssl.com/',
            'https://wrong.host.badssl.com/',
            ):
    try:
        webpage = urlopen(url)
    except (IOError, ValueError):
        print ('URL %r could not be opened: %s' % (url, sys.exc_info()))
        failures += 1
        continue
    else:
        print ('URL %r could be opened, even though it is not trusted' %
               url)
    data = webpage.read(chunk)
    assert len(data) == chunk, 'URL %s did not return enough data' % url
    webpage.close()
if PYTHON_VERSION < (2, 7):
    assert failures == 0
elif not int(os.environ.get('PYRUN_HTTPSVERIFY', 1)):
    print ('Note: PYRUN_HTTPSVERIFY is set to 0')
    assert failures == 0
else:
    assert failures == 3

print ('')
print ('Works.')
print ('')
