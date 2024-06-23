# eGenix PyRun

[eGenix PyRun](https://pyrun.org) is an open source, compressed, single
file Python compatible run-time, which fits into merely 5 MB on disk.

It can be used to ship pure Python products as a single file on Unix
platforms, to create Python Docker images with very small footprint to speed
up deployment, or as a neat venv replacement, truly isolating applications
from any OS or other Python installations.

We have been using PyRun internally for many years and open sourced it back
in 2012, when it was well received and grew a small fan base. In 2024, we
are moving the project from our in-house mono-repo to Github and relaunching
it, in order to present it to the wider open source and Python community.

# Support Python Versions

PyRun currently (actively) supports these Python releases on Unix platforms:

- Python 3.8
- Python 3.9
- Python 3.10
- Python 3.11

For each release, only one patch level version is supported,
since PyRun has to patch to the Python source code in order to
implement extensions needed to make PyRun more compatible with
standard Python.

Please see the top of the `Makefile` for the patch level releases supported
by this release of eGenix PyRun.

Note: PyRun has a long history and includes references to several additional
Python releases, but we only actively support the above subset of those at
the moment.

## Removal of supported versions

We usualy remove active support for Python versions after [they have
been end-of-lifed](https://devguide.python.org/versions/), ie. no longer
receive security releases.

# Build Dependencies

The following development packages need to be installed on the build system
in addition to the compiler suite (names could be slightly different for
your system):

- libbz2-devel
- sqlite3-devel
- openssl-devel
- zlib-devel

The tests need a few extra libs:

- libxml2-devel
- libxslt-devel

# Building

`make build-all` will build eGenix PyRun for all supported Python
releases and place the results into the 'build-\*' directories.

If you want to create distribution files instead, use
`make all-distributions`.

For building just one Python release target, you have to specify
the PYTHONFULLVERSION on the make command line:

`make build PYTHONFULLVERSION=3.10.13`

or

`make distribution PYTHONFULLVERSION=3.10.13`

# Testing

The Makefile has various test targets.

- `make test-basic` will test the basic functionality of eGenix PyRun.

- `make test-pip` can be used to test eGenix PyRun against various
  packages downloaded using pip.

- `make test-distribution` runs both test-basic and test-pip.

- `make test-all-distributions` will run test-distribution for all
  supported Python releases.

- `make test-all-pyruns` will run test-basic for all supported Python
  releases.

- `make test-ssl` tests the PYRUN_HTTPSVERIFY env var.

# Roadmap

We have big plans for eGenix PyRun. These are some of the things we have
planned:

- Support for Python 3.11 and 3.12 (and beyond)

- Creation of a CLI to more easily install and use PyRun, which will
  eventually replace the bash script install-pyrun.

- Provision of Alpine based Docker containers with PyRun (instead of a
  full CPython installation) for use in testing, production and as basis
  for truly isolated Python based applications.

and longer term:

- Exploring support for new platforms such as Windows or Emscripten.

# License

eGenix PyRun itself is made available under the [Apache 2.0
license](http://www.apache.org/licenses/LICENSE-2.0) (see
COPYRIGHT.NOTICE for details).

Since PyRun is based on Python and creates a custom distribution of
Python, the resulting binaries are covered by the combination of the
Apache 2.0 license, the Python license (see LICENSE.Python) and other
3rd licenses included in the Python source distribution. The `pyrun/`
source directory contains the patches we apply to the Python
distribution.

# Commercial Support

eGenix PyRun is brought to you by [eGenix.com Software, Skills and
Services GmbH](https://egenix.com), your boutique consulting and open
source specialist, with a strong focus on Python, databases and large
scale data applications.

Please [contact us](mailto:sales@egenix.com) for more information.
