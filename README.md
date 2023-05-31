# eGenix PyRun

PyRun currently (actively) supports these Python releases:

 * Python 3.7
 * Python 3.8
 * Python 3.9
 * Python 3.10

For each release, only one patch level version is supported,
since PyRun has to patch to the Python source code in order to
implement extensions needed to make PyRun more compatible with
standard Python.

Please see the top of the Makefile for the patch level releases
supported by this release of eGenix PyRun.

Note: PyRun has a long history and includes references to several more
Python releases, but we only actively support the above subset of those.

# Build Dependencies

The following development packages need to be installed on the build system
in addition to the compiler suite (names could be slightly different for
your system):

 * libbz2-devel
 * sqlite3-devel
 * openssl-devel
 * zlib-devel

The tests need a few extra libs:

 * libxml2-devel
 * libxslt-devel

# Building

"make build-all" will build eGenix PyRun for all supported Python
releases and place the results into the build-* directories.

If you want to create distribution files instead, use
"make all-distributions".

For building just one Python release target, you have to specify
the PYTHONFULLVERSION on the make command line:

make build PYTHONFULLVERSION=3.10.11

or

make distribution PYTHONFULLVERSION=3.10.11

# Testing

The Makefile has various test targets.

"make test-basic" will test the basic functionality of eGenix PyRun.

"make test-pip" can be used to test eGenix PyRun against various
packages downloaded using pip.

"make test-distribution" runs both test-basic and test-pip.

"make test-all-distributions" will run test-distribution for all
supported Python releases.

"make test-all-pyruns" will run test-basic for all supported Python
releases.

"make test-ssl" tests the PYRUN_HTTPSVERIFY env var.
