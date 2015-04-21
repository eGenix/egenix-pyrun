""" Test SSL and HTTPS connectivity of pyrun.

"""

import sys
PYTHON_VERSION = sys.version_info
PY3 = (PYTHON_VERSION[0] == 3)

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
    
print ('Works.')
