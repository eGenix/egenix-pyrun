<div align="center" style="margin-bottom: 2em">
  <p style="margin-bottom: 1em">eGenix proudly presents:</p>
  <img alt="eGenix PyRun Logo" src="docs/logo-with-text.svg" width="500">
  <p style="margin-top: 1em"><i>Your friendly, lean, open source Python runtime</i></p>
</div>

[eGenix PyRun](https://pyrun.org) is an Apache licensed, compressed,
single file [Python}(https://python.org/) compatible run-time, which
fits into merely 5-6 MB on disk.

It can be used to ship pure Python products as a single file on Unix
platforms, to create Python Docker images with very small footprint to speed
up deployment, or as a neat venv replacement, truly isolating applications
from any OS or other Python installations.

We have been using PyRun internally for many years and open sourced it back
in 2012, when it was well received and grew a small fan base. In 2024, we
are moving the project from our in-house mono-repo to Github and relaunching
it, in order to present it to the wider open source and Python community.

## Binary sizes

Since PyRun is all about reducing the deployment footprint, here are
some numbers for recent versions:

```
-rwxr-xr-x 1 lemburg lemburg 5.5M Jun 25 15:48 pyrun3.11
-rwxr-xr-x 1 lemburg lemburg 4.8M Jun 25 14:16 pyrun3.10
-rwxr-xr-x 1 lemburg lemburg 4.9M Jun 25 13:47 pyrun3.9
-rwxr-xr-x 1 lemburg lemburg 4.8M Jun 25 13:38 pyrun3.8
```

As you can see, Python's footprint has grown a bit recently. The major
jump between 3.10 and 3.11 is due to the new byte code VM, which makes
Python a lot faster compared to previous versions. It's a classical
size-runtime tradeoff, but well worth it.

The small file sizes are the result of freezing most of the Python
stdlib directly into the binary, compiling most stdlib C extensions
statically, stripping debug information and running the
[executable compressor upx](https://upx.github.io/) against the
resulting binary.

# Supported Python Versions

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
been end-of-life'd](https://devguide.python.org/versions/), ie. no longer
receive security releases.

# Building PyRun

## Build Dependencies

The following development packages need to be installed on the build system
in addition to the compiler suite (names could be slightly different for
your system):

- libbz2-devel
- sqlite3-devel
- openssl-devel
- zlib-devel
- upx

The tests need a few extra libs:

- libxml2-devel
- libxslt-devel

If you want to get some extra compression, you can download the latest upx
version available on [executable compressor upx](https://upx.github.io/).

## Building

`make build-all` will build eGenix PyRun for all supported Python
releases and place the results into the `build/` subdirectories.

If you want to create distribution files instead, use
`make all-distributions`.

For building just one Python release target, you have to specify the
`PYTHONFULLVERSION` variable on the make command line (using the full
patch level version, as the name suggests):

```
make build PYTHONFULLVERSION=3.11.9
```
or
```
make distribution PYTHONFULLVERSION=3.11.9
```

The build process will download the Python tarball if needed. Please see the `Makefile` for details.

## Testing

The `Makefile` has various test targets.

- `make test-basic` will test the basic functionality of eGenix PyRun.

- `make test-pip` can be used to test eGenix PyRun against various
  packages downloaded using pip.

- `make test-distribution` runs both test-basic and test-pip.

- `make test-all-distributions` will run test-distribution for all
  supported Python releases.

- `make test-all-pyruns` will run test-basic for all supported Python
  releases.

- `make test-ssl` tests the PYRUN_HTTPSVERIFY env var.

It is also possible to run the complete Python test suite, but not
directly supported by the `Makefile` yet.

Please note that some tests will fail due to the way PyRun works:

- Files embedded into Python packages are not available when frozen into
  the PyRun binary.

- Embedding PyRun is not supported. As a result `test_embed` fails.

- PyRun does not implement the entire set of command line options of
  CPython, but most environment variables work as expected. See `pyrun
  -h` for a list of available command line options.

There are a few more limitations, which we will list in the docs once we
have them available on Github.

# Installing PyRun

There are multiple ways to "install" PyRun. All variants simply copy
files around. There is no OS installation in the classical sense (and that's
a feature).

## Installation from distribution archives

Simply untar the distribution archives where you need them.

The archives include everything required to run PyRun, including shared
modules which we don't include in the main binary and the include files
which are needed if you want to use PyRun to build extensions.

```
> tar xfz egenix-pyrun-2.5.0-py3.11_ucs4-linux-x86_64.tgz
> bin/pyrun
eGenix PyRun 3.11.9 (release 2.5.0, main, Jun 25 2024, 14:27:19) [GCC 7.5.0]
Thank you for using eGenix PyRun. Type "help" or "license" for details.

>>>
```

## Installation from sources

The source `Makefile` includes a target `install` which will install
PyRun into `/usr/local`. The prefix can be adjusted by passing
`PREFIX=/path` to `make`.

```
> make install
> /usr/local/bin/pyrun
eGenix PyRun 3.11.9 (release 2.5.0, main, Jun 25 2024, 14:27:19) [GCC 7.5.0]
Thank you for using eGenix PyRun. Type "help" or "license" for details.

>>>
```

This will install the same files as you find in the distribution
archives.

## Installation using just the pyrun binary

The binary with the one file runtime is called `pyrunX.X`, with X.X
marking the supported Python version, e.g. `pyrun3.11` for the Python
3.11 edition.

You can simply copy this file to you app dir and then use it right away.

The file can be extracted from the distribution archives. Just make sure
you extract it from the right archive for your platform.

It's also possible to build it locally, using the source distribution,
by running:

```
> make runtime
```

The Makefile will print out the location where you can pick up the file.

## Runtime dependencies

PyRun currently has the following runtime dependencies, which should be
easy to fullfil on most Unix platforms (the names of the shared libaries
may be different depending on the target OS):

- libm.so # Math library
- libz.so # zlib support
- libbz2.so # bzip2 support
- libsqlite3.so # SQLite support
- libssl.so # OpenSSL
- libcrypto.so # OpenSSL

in addition to the standard lib C ones.

# Roadmap

PyRun has been around for a long while, but we still have big plans for
eGenix PyRun, especially now that development can happen in a new repo
on Github.

These are some of the things we have planned:

## Short term

- Add CI/CD to have PyRun automatically built on various architectures

- Add more documentation

- Support for Python 3.12 and 3.13

## Medium term

- Keep updating PyRun to support new Python versions.

- Creation of a CLI to more easily install and use PyRun, which will
  eventually replace the bash script `install-pyrun` and offer easy ways
  to create single file apps for Unix platforms.

- Provision of Alpine based Docker containers with PyRun (instead of a
  full CPython installation) for use in testing, production and as basis
  for truly isolated Python based applications.

## Longer term

- Exploring support for new platforms such as Windows or Emscripten.
  Perhaps we can get this by using the [cross-compilation tools from
  Zig](https://zig.guide/build-system/cross-compilation).

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

# Version history

## 2.5.0

- Added support for Python 3.11
- Removed support for Python 3.5-3.7
- Modernized the directory setup and build
- Changed the license to the Apache2 license
- Extracted the code from our internal mono-repo to put on Github

## 2.4.0

- Added support for Python 3.9 and 3.10
- This version was not released.

## Earlier versions

- Support for Python 3.6-3.8 was added over the years, but not released.
- Please see the [changelog](https://www.egenix.com/products/python/PyRun/changelog.html)
  on the eGenix website for details.
