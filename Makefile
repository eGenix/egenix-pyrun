# Makefile for eGenix PyRun
#
# Usage:
#
#     make
#     make install
#
# Default is to install pyrun under the /usr/local prefix. The
# "make install" command puts the interpreter into /usr/local/bin
# as pyrunX.X and any extra libs into /usr/local/lib/pyrunX.X.
# With X.X referring to the Python version.
#
# The default prefix can be changed using "make install PREFIX=/path".
#
# Default is to build Python version PYTHONFULLVERSION. This can be changed
# by adding "PYTHONFULLVERSION=x.x.x" to both make command lines or editing
# this file.
#
# Note that this Makefile needs GNU make. On some operating systems
# this is installed as "gmake".
#

### High-level configuration

# Python versions to use for pyrun
#
# Latest as of 2024-06-19:
PYTHON_311_VERSION = 3.11.9
PYTHON_310_VERSION = 3.10.14
PYTHON_39_VERSION = 3.9.19
PYTHON_38_VERSION = 3.8.19
PYTHON_37_VERSION = 3.7.17
PYTHON_36_VERSION = 3.6.15
PYTHON_27_VERSION = 2.7.18

# Python version to use as basis for pyrun (select a default one)
PYTHONFULLVERSION = $(PYTHON_311_VERSION)
#PYTHONFULLVERSION = $(PYTHON_310_VERSION)
#PYTHONFULLVERSION = $(PYTHON_39_VERSION)
#PYTHONFULLVERSION = $(PYTHON_38_VERSION)
#PYTHONFULLVERSION = $(PYTHON_37_VERSION)
#PYTHONFULLVERSION = $(PYTHON_36_VERSION)
#PYTHONFULLVERSION = $(PYTHON_27_VERSION)

# All supported target versions:
PYTHONVERSIONS = \
	$(PYTHON_38_VERSION) \
	$(PYTHON_39_VERSION) \
	$(PYTHON_310_VERSION) \
	$(PYTHON_311_VERSION)

# All available versions:
ALLPYTHONVERSIONS = \
	$(PYTHON_27_VERSION) \
	$(PYTHON_36_VERSION) \
	$(PYTHON_37_VERSION) \
	$(PYTHON_38_VERSION) \
	$(PYTHON_39_VERSION) \
	$(PYTHON_310_VERSION) \
	$(PYTHON_311_VERSION)

# Python Unicode version
#
# Only needed for Python 2 and early Python 3.x versions
#
PYTHONUNICODE = ucs2

# Python 3 ABI flags (see PEP 3149)
#
# These should probably be determined by running a standard Python 3 and
# checking sys.abiflags. Hardcoding them here for now, since they rarely
# change.
#
# The ABI flags were only used in paths for Python 3.x - 3.7. Python
# 3.8+ no longer use these flags for e.g. include file paths.
#
PYTHONABI = m

# Packages and modules to exclude from the runtime (note that each
# module has to be prefixed with "-x ") for both Python 2 and 3.  Note
# that makepyrun.py has its own predefined list of modules to exclude
# in the module search. This list of excludes provides extra
# protection against modules which are still found by the search and
# should not be included in pyrun. They can also be used to further
# trim down the module/package list, if needed.
#
EXCLUDES = 	-x test \
		-x Tkinter \
		-x tkinter \
		-x setuptools \
		-x pydoc_data \
		-x pip

# Package details (used for distributions and normally passed in via
# the product Makefile)
PACKAGENAME = egenix-pyrun

# Package version
#
# Note that you have to keep this in sync with runtime/makepyrun.py
#
PACKAGEVERSION = 2.5.0
#PACKAGEVERSION = $(shell cd runtime; python -c "from makepyrun import __version__; print __version__")

# OpenSSL installation to compile and link against. If an environment
# variable SSL is given we use that.  Otherwise, We check a few custom
# locations which possibly more recent versions before going to the standard
# system paths.  /usr/local is common on Linux, /usr/contrib on HP-UX,
# /usr/sfw on Solaris/OpenIndiana, fallback is /usr.
PYRUN_SSL := $(shell if ( test -n "$(SSL)" ); then echo $(SSL); \
		    elif ( test -e /usr/include/openssl/ssl.h ); then echo /usr; \
		    elif ( test -e /usr/local/ssl/include/openssl/ssl.h ); then echo /usr/local/ssl; \
		    elif ( test -e /usr/contrib/ssl/include/openssl/ssl.h ); then echo /usr/contrib/ssl; \
		    elif ( test -e /usr/sfw/include/openssl/ssl.h ); then echo /usr/sfw; \
		    else echo /usr; \
		    fi)
SSL = $(PYRUN_SSL)
export SSL

### runtime build parameters

# Project dir
PWD := $(shell pwd)

# Version & Platform
PYTHONVERSION := $(shell echo $(PYTHONFULLVERSION) | sed 's/\([0-9]\.[0-9]\+\).*/\1/')
PYTHONMAJORVERSION := $(shell echo $(PYTHONFULLVERSION) | sed 's/\([0-9]\+\)\..*/\1/')
PYTHONMINORVERSION := $(shell echo $(PYTHONFULLVERSION) | sed 's/[0-9]\.\([0-9]\+\)\..*/\1/')
PYRUNFULLVERSION = $(PYTHONFULLVERSION)
PYRUNVERSION = $(PYTHONVERSION)
PLATFORM := $(shell uname -s -m | sed 's/ /-/g' | tr '[:upper:]' '[:lower:]')

# Python build flags
PYTHON_2_BUILD := $(shell test "$(PYTHONMAJORVERSION)" = "2" && echo "1")
PYTHON_27_BUILD := $(shell test "$(PYTHONVERSION)" = "2.7" && echo "1")
PYTHON_3_BUILD := $(shell test "$(PYTHONMAJORVERSION)" = "3" && echo "1")
PYTHON_36_BUILD := $(shell test "$(PYTHONVERSION)" = "3.6" && echo "1")
PYTHON_37_BUILD := $(shell test "$(PYTHONVERSION)" = "3.7" && echo "1")
PYTHON_37_OR_EARLIER_BUILD := $(shell test $(PYTHONMAJORVERSION) -eq 3 && test $(PYTHONMINORVERSION) -le 7 && echo "1")
PYTHON_38_BUILD := $(shell test "$(PYTHONVERSION)" = "3.8" && echo "1")
PYTHON_39_BUILD := $(shell test "$(PYTHONVERSION)" = "3.9" && echo "1")
PYTHON_39_OR_EARLIER_BUILD := $(shell test $(PYTHONMAJORVERSION) -eq 3 && test $(PYTHONMINORVERSION) -le 9 && echo "1")
PYTHON_310_BUILD := $(shell test "$(PYTHONVERSION)" = "3.10" && echo "1")
PYTHON_310_OR_LATER_BUILD := $(shell test $(PYTHONMAJORVERSION) -eq 3 && test $(PYTHONMINORVERSION) -ge 10 && echo "1")
PYTHON_311_BUILD := $(shell test "$(PYTHONVERSION)" = "3.11" && echo "1")
PYTHON_311_OR_LATER_BUILD := $(shell test $(PYTHONMAJORVERSION) -eq 3 && test $(PYTHONMINORVERSION) -ge 11 && echo "1")

# Special Python environment setups

ifdef PYTHON_3_BUILD
 # We support Python 3.5+ only, which no longer has different versions
 # for Unicode. Since PYTHONUNICODE is used in a lot of places, we
 # simply assign a generic term to it for Python 3.
 PYTHONUNICODE := ucs4
endif

ifdef PYTHON_310_OR_LATER_BUILD
 # distutils still has a dependency on lib2to3, so force exclusion:
 EXCLUDES +=	-x lib2to3
endif

# Setuptools' embedded distutils has a bug in the loader which causes it
# not to work with pyrun for Python 3.8 and 3.9, so disable using the
# embedded copy:
ifdef PYTHON_39_OR_EARLIER_BUILD
 SETUPTOOLS_USE_DISTUTILS = stdlib
 export SETUPTOOLS_USE_DISTUTILS
endif

# Name of the resulting pyrun executable
PYRUN_GENERIC = pyrun
PYRUN = $(PYRUN_GENERIC)$(PYRUNVERSION)
PYRUN_DEBUG = $(PYRUN)-debug
PYRUN_STANDARD = $(PYRUN)-standard
PYRUN_UPX = $(PYRUN)-upx

# Symlinks to create for better Python compatibility
ifdef PYTHON_2_BUILD
 PYRUN_SYMLINK_GENERIC = python
 PYRUN_SYMLINK = python$(PYTHONVERSION)
else
 PYRUN_SYMLINK_GENERIC = python3
 PYRUN_SYMLINK = python$(PYTHONVERSION)
endif

# Archive name to create with "make archive"
ARCHIVE = $(PYRUN)-$(PYRUNFULLVERSION)-$(PLATFORM)

# Location of the Python tarball
PYTHONTARBALL = /downloads/python/Python-$(PYTHONFULLVERSION).tgz
PYTHONSOURCEURL = https://www.python.org/ftp/python/$(PYTHONFULLVERSION)/Python-$(PYTHONFULLVERSION).tgz

# Base dir used for a PyRun build
BASEDIR = $(PWD)/build/$(PYTHONVERSION)-$(PYTHONUNICODE)

# Python source directories
PYTHONORIGDIR = $(BASEDIR)/Python-$(PYTHONFULLVERSION)
PYTHONDIR = $(BASEDIR)/python-build
# PYTHONORIGDIFFDIR is PYTHONORIGDIR relative to PYTHONDIR and used for
# creating patches
PYTHONORIGDIFFDIR = ../Python-$(PYTHONFULLVERSION)

# PyRun source directories
PYRUNSOURCEDIR = $(PWD)/pyrun
# PYRUNDIR is a copy of PYRUNSOURCEDIR used to freeze pyrun
PYRUNDIR = $(BASEDIR)/pyrun-build
ifdef PYTHON_2_BUILD
 FREEZEDIR = $(PYRUNDIR)/freeze-2
else
 FREEZEDIR = $(PYRUNDIR)/freeze-3
endif

# PyRun C compiler optimization settings
PYRUN_OPT := -g -O3 -Wall -Wstrict-prototypes
OPT = $(PYRUN_OPT)
export OPT

# Freeze optimization settings; the freeze.py script is run with these
# Python optimization settings, which affect the way the stdlib modules are
# compiled. Note that user code will not automatically use these settings.
#
# Produce optimized code, with debug and assertions disabled.
PYRUNFREEZEOPTIMIZATION = -O
#
# Produce optimized code, with doc-string removed, debug and assertions
# disabled.  This results in a reduction of the compressed PyRun size of
# about 8%, compared to -O.
#PYRUNFREEZEOPTIMIZATION = -OO

# Starting with Python 3.11, fine grained error location reporting was
# added. This requires a lot of extra space for storing the char-in-line
# information and contributes a lot to the size of the binary.
#
# We disable creating those debug ranges for PyRun itself, but leave it
# enabled for when using PyRun. Use the PYTHONNODEBUGRANGES env var to
# disable this for code using PyRun as well - when running the code.
ifdef PYTHON_311_OR_LATER_BUILD
 PYRUNFREEZEDEBUGRANGES = -X no_debug_ranges
else
 PYRUNFREEZEDEBUGRANGES =
endif

# Name of the freeze template and executable
PYRUNPY = $(PYRUN).py

# Name of the special eGenix PyRun Modules/Setup file
MODULESSETUP = Setup.PyRun-$(PYTHONVERSION)

# Name of the target Modules/Setup file
ifdef PYTHON_311_OR_LATER_BUILD
 # The logic changed in 3.11 to use Setup.local instead of editing Setup
 # directly
 MODULESSETUPTARGET = Setup.local
else
 MODULESSETUPTARGET = Setup
endif

# Name of the pyrun Python patch file
PYTHONPATCHFILE = Python-$(PYTHONVERSION).patch

# Name of the temporary full Python installation target dir; this is where
# the patched Python version will get installed prior to using it for
# freezing pyrun.
FULLINSTALLDIR = $(BASEDIR)/python-installation
FULLPYTHON = $(FULLINSTALLDIR)/bin/python$(PYTHONVERSION)
FULLLIBDIR = $(FULLINSTALLDIR)/lib/python$(PYTHONVERSION)
FULLSHAREDLIBDIR = $(FULLLIBDIR)/lib-dynload
FULLSITEPACKAGESLIBDIR = $(FULLLIBDIR)/site-packages
ifdef PYTHON_2_BUILD
 # Python 2.x did not have ABI dirs
 FULLINCLUDEDIR = $(FULLINSTALLDIR)/include/python$(PYTHONVERSION)
else ifdef PYTHON_37_OR_EARLIER_BUILD
 # Python 3.x - 3.7 put the include files into an ABI specific dir
 FULLINCLUDEDIR = $(FULLINSTALLDIR)/include/python$(PYTHONVERSION)$(PYTHONABI)
else
 # Python 3.8 returned to the non-ABI dir
 FULLINCLUDEDIR = $(FULLINSTALLDIR)/include/python$(PYTHONVERSION)
endif

# Path prefix to use in byte code files embedded into the frozen pyrun
# binary instead of the build time one
PYRUNLIBDIRCODEPREFIX = "$(FULLLIBDIR)=<pyrun>"
PYRUNDIRCODEPREFIX = "$(PYRUNDIR)=<pyrun>"

# PyRun build dir.  This is used to prepare all the PyRun parts for
# installation.  It is used by `make install` as source of the build files.
BUILDDIR = $(BASEDIR)/pyrun-installation

# Target dir of binaries
BINDIR = $(BUILDDIR)/bin

# Target dir of shared modules
LIBDIR = $(BUILDDIR)/lib
PYRUNLIBDIR = $(LIBDIR)/python$(PYRUNVERSION)
PYRUNSHAREDLIBDIR = $(PYRUNLIBDIR)/lib-dynload
PYRUNSITEPACKAGESLIBDIR = $(PYRUNLIBDIR)/site-packages

# Target dir for include files
INCLUDEDIR = $(BUILDDIR)/include
ifdef PYTHON_2_BUILD
 # Python 2.x did not have ABI dirs
 PYRUNINCLUDEDIR = $(INCLUDEDIR)/python$(PYRUNVERSION)
else ifdef PYTHON_37_OR_EARLIER_BUILD
 # Python 3.x - 3.7 put the include files into an ABI specific dir
 PYRUNINCLUDEDIR = $(INCLUDEDIR)/python$(PYRUNVERSION)$(PYTHONABI)
else
 # Python 3.8 returned to the non-ABI dir
 PYRUNINCLUDEDIR = $(INCLUDEDIR)/python$(PYRUNVERSION)
endif

# Target dir for PyRun binary distribution builds.  This is used to create a
# directory structure which is then tar'ed to create the PyRun binary
# bundles.
DISTBUILDDIR  = $(BASEDIR)/pyrun-dist

# PyRun rpath setting (used to hardwire linker paths into the binary)
#
# See man ld for details. $ORIGIN refers to the location of the binary
# at run time. This can be used to avoid having to set LD_LIBRARY_PATH
# before invking pyrun.
#
# $ORIGIN
#     First look up shared libs in the same dir as pyrun. This
#     mimics the logic used on Windows for EXEs.
# $ORIGIN/../lib
#     This setting allows easily shipping external shared libs
#     together with pyrun in the lib/ dir
# $ORIGIN/../lib/pythonX.X/site-packages/OpenSSL
#     We use this to enable using egenix-pyopenssl with pyrun and without
#     having to set LD_LIBRARY_PATH
#
# Use the "show-rpath" target for debugging purposes.
#
PYRUNORIGIN = \$$ORIGIN
PYRUNRPATH := $(PYRUNORIGIN):$(PYRUNORIGIN)/../lib:$(PYRUNORIGIN)/../lib/python$(PYRUNVERSION)/site-packages/OpenSSL

# Install all binaries, or just the default ones ?  Set to 1 to enable this.
INSTALLALLBINARIES =

# Installation directories
PREFIX = /usr/local
INSTALLBINDIR = $(PREFIX)/bin
INSTALLLIBDIR = $(PREFIX)/lib
INSTALLSHAREDLIBDIR = $(INSTALLLIBDIR)/lib-dynload
INSTALLINCLUDEDIR = $(PREFIX)/include

# Binary distributions
DISTDIR = $(PWD)/dist
BINARY_DISTRIBUTION = $(PACKAGENAME)-$(PACKAGEVERSION)-py$(PYTHONVERSION)_$(PYTHONUNICODE)-$(PLATFORM)
BINARY_DISTRIBUTION_ARCHIVE = $(DISTDIR)/$(BINARY_DISTRIBUTION).tgz

# Test directory used for running tests
TESTDIR = $(PWD)/testing-$(PYTHONVERSION)-$(PYTHONUNICODE)

# Directory with PyRun tests
PYRUNTESTS = $(PWD)/tests

# Python configure options

# Regular builds
PYTHON_DEFAULT_CONFIGURE_OPTIONS = "--enable-optimizations"
#PYTHON_DEFAULT_CONFIGURE_OPTIONS = "--enable-optimizations --with-lto=yes"
# Dev builds, which don't need to be optimized
PYTHON_DEV_CONFIGURE_OPTIONS = ""

# ... use the default options for regular builds
PYTHON_CONFIGURE_OPTIONS = $(PYTHON_DEFAULT_CONFIGURE_OPTIONS)

# Build platform
LINUX_PLATFORM := $(shell test "`uname -s`" = "Linux" && echo "1")
MACOSX_PLATFORM := $(shell test "`uname -s`" = "Darwin" && echo "1")
MACOSX_PPC_PLATFORM := $(shell test "`uname -s -p`" = "Darwin powerpc" && echo "1")
MACOSX_INTEL_PLATFORM := $(shell test "`uname -s -p`" = "Darwin i386" && echo "1")
FREEBSD_PLATFORM := $(shell test "`uname -s`" = "FreeBSD" && echo "1")
RASPI_PLATFORM := $(shell test "`uname -s -m`" = "Linux armv6l" && echo "1")

# Special OS environment setups
ifdef MACOSX_PPC_PLATFORM
 # On PPC Macs, we use the 10.4 SDK to build universal PPC/i386 binaries
 export MACOSX_DEPLOYMENT_TARGET=10.4
 PYTHON_CONFIGURE_OPTIONS = --enable-universalsdk MACOSX_DEPLOYMENT_TARGET=10.4
endif
ifdef MACOSX_INTEL_PLATFORM
 # On Intel Macs, we use the 10.5 SDK to build x86_64 binaries
 export MACOSX_DEPLOYMENT_TARGET=10.5
 PYTHON_CONFIGURE_OPTIONS = MACOSX_DEPLOYMENT_TARGET=10.5
endif

# Tools
TAR = tar
# MAKE is a predefined variable
RM = /bin/rm
STRIP = strip
CP = cp -p
CP_DIR = cp -pR
CHMOD = chmod
WGET = wget
TPUT = tput
ECHO = /bin/echo -e
UPX := $(shell which upx 2> /dev/null)
UPXOPTIONS = -9 -qqq

ifdef MACOSX_PLATFORM
ECHO = /bin/echo
TPUT = tput -T xterm
endif

ifdef FREEBSD_PLATFORM
ECHO = /bin/echo
# MAKE = gmake # We need gmake on FreeBSD
endif

ifdef RASPI_PLATFORM
TPUT = tput -T xterm
endif

# Stripping the executable
#
# Note: strip on Macs strips too much information from the executable
# per default, rendering the resulting executable unusable for dynamic
# linking. See #792. Use -S to only strip the debug information like
# on Linux
STRIPOPTIONS = -S

# ANSI screen codes
BOLD := `$(TPUT) bold`
OFF := `$(TPUT) sgr0`

# Build logs
DATE := $(shell date +'%Y-%m-%d-%H%M%S')
TODAY := $(shell date +'%Y-%m-%d')
BUILDLOGDIR = build-logs
BUILDLOG = $(BUILDLOGDIR)/$(BINARY_DISTRIBUTION)-$@-$(DATE).log
BUILDLOGGZ = $(BUILDLOG).gz
LOGREDIR =  2>&1 | tee $(BUILDLOG); gzip $(BUILDLOG); $(ECHO) "Wrote build log to $(BUILDLOGGZ)"; $(ECHO) ""
TODAYSBUILDLOGS = $(BUILDLOGDIR)/*-$(TODAY)-*.log*

### Generic targets

all:	pyrun

pyrun:	config interpreter runtime

### Logging

logs:
	mkdir -p $(BUILDLOGDIR)

check-build-logs:
	zgrep -n -i -E -C 2 --color=always '(make.*[*][*][*]|error +[0-9]+| +failed[^"])' $(TODAYSBUILDLOGS) | less

### Announcements

announce-distribution:
	@$(ECHO) ""
	@$(ECHO) "==============================================================================="
	@$(ECHO) "$(BOLD)Building $(PACKAGENAME) $(PACKAGEVERSION) for Python $(PYTHONFULLVERSION)-$(PYTHONUNICODE) $(OFF)"
	@$(ECHO) "-------------------------------------------------------------------------------"
	@$(ECHO) ""

### Version updates

update-product-version:
	$(ECHO) "Updating version to $(PACKAGEVERSION) in install-pyrun"
	sed -i -r --follow-symlinks \
		-e "s/pyrun=[0-9.]+/pyrun=$(PACKAGEVERSION)/" \
		-e "s/PyRun version [0-9.]+/PyRun version $(PACKAGEVERSION)/" \
		-e "s/PYRUN_VERSION=[0-9.]+/PYRUN_VERSION=$(PACKAGEVERSION)/" \
		install-pyrun
	$(ECHO) "Updating version to $(PACKAGEVERSION) in makepyrun.py"
	sed -i -r --follow-symlinks \
		-e "s/__version__ = '[^']*'/__version__ = '$(PACKAGEVERSION)'/" \
		$(PYRUNDIR)/makepyrun.py

### Build process

$(BASEDIR):
	mkdir -p $(BASEDIR)

$(PYTHONORIGDIR):
	cd $(BASEDIR); \
	if test -z $(PYTHONTARBALL) || ! test -e $(PYTHONTARBALL); then \
	    $(ECHO) "Downloading and extracting $(PYTHONSOURCEURL)."; \
	    $(WGET) -O - $(PYTHONSOURCEURL) | tar xz ; \
	else \
	    $(ECHO) "Extracting local copy $(PYTHONTARBALL)."; \
	    $(TAR) xfz $(PYTHONTARBALL) ; \
	fi

python-orig:	$(PYTHONORIGDIR)

$(PYTHONDIR):	$(BASEDIR) $(PYTHONORIGDIR) $(PYRUNSOURCEDIR)/$(PYTHONPATCHFILE)
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Setting up the Python sources ============================================="
	@$(ECHO) "$(OFF)"
	$(RM) -rf $(PYTHONDIR)
        # Copy orig source dir to $(PYTHONDIR)
	$(CP_DIR) $(PYTHONORIGDIR) $(PYTHONDIR)
        # Apply Python patches needed for pyrun
	cd $(PYTHONDIR); \
	patch -p0 -F10 < $(PYRUNSOURCEDIR)/$(PYTHONPATCHFILE)
	touch $@

sources: $(PYTHONDIR)

# Note: The dependency is on the Python patchlevel.h file, not the
# source directory.  This is to avoid unnecessary rebuilds in case the
# source directory changes for whatever reason during builds.

$(PYTHONDIR)/Include/patchlevel.h:	$(PYTHONDIR)

ifdef PYTHON_2_BUILD
$(PYTHONDIR)/pyconfig.h:	$(PYTHONDIR)/Include/patchlevel.h
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Configuring Python ========================================================"
	@$(ECHO) "$(OFF)"
	cd $(PYTHONDIR); \
	CONFIG_SITE="" \
	./configure \
		--prefix=$(FULLINSTALLDIR) \
		--exec-prefix=$(FULLINSTALLDIR) \
		--libdir=$(FULLINSTALLDIR)/lib \
		--enable-unicode=$(PYTHONUNICODE) \
		$(PYTHON_CONFIGURE_OPTIONS)
else
$(PYTHONDIR)/pyconfig.h:	$(PYTHONDIR)/Include/patchlevel.h
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Configuring Python ========================================================"
	@$(ECHO) "$(OFF)"
	cd $(PYTHONDIR); \
	CONFIG_SITE="" \
	./configure \
		--prefix=$(FULLINSTALLDIR) \
		--exec-prefix=$(FULLINSTALLDIR) \
		--libdir=$(FULLINSTALLDIR)/lib \
		--without-ensurepip \
		$(PYTHON_CONFIGURE_OPTIONS)
endif

config:	$(PYTHONDIR)/pyconfig.h

$(PYTHONDIR)/Makefile: $(PYTHONDIR)/pyconfig.h $(PYRUNSOURCEDIR)/$(MODULESSETUP)
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Setting up the Python modules ============================================="
	@$(ECHO) "$(OFF)"
        # Create full install dir structure
	if test -d $(FULLINSTALLDIR); then $(RM) -rf $(FULLINSTALLDIR); fi
	mkdir -p $(FULLINSTALLDIR) $(FULLINSTALLDIR)/lib $(FULLINSTALLDIR)/bin \
		 $(FULLINSTALLDIR)/include
        # Install the custom "Modules/Setup" file
	if test "$(MACOSX_PLATFORM)"; then \
		sed 	-e 's/# @if macosx: *//' \
			$(PYRUNSOURCEDIR)/$(MODULESSETUP) \
			> $(PYTHONDIR)/Modules/$(MODULESSETUPTARGET); \
	elif test "$(FREEBSD_PLATFORM)"; then \
		sed 	-e 's/# @if freebsd: *//' \
			$(PYRUNSOURCEDIR)/$(MODULESSETUP) \
			> $(PYTHONDIR)/Modules/$(MODULESSETUPTARGET); \
	else \
		sed 	-e 's/# @if not macosx: *//' \
			-e 's/# @if not freebsd: *//' \
			$(PYRUNSOURCEDIR)/$(MODULESSETUP) \
			> $(PYTHONDIR)/Modules/$(MODULESSETUPTARGET); \
	fi;
        # Recreate the Makefile after the above changes
	cd $(PYTHONDIR); \
	$(RM) -f Makefile; \
	$(MAKE) -f Makefile.pre Makefile

modules:	$(PYTHONDIR)/Makefile

$(BUILDDIR):	$(BASEDIR)
	# Create the PyRun install dir structure
	mkdir -p	$(BUILDDIR) \
			$(BINDIR) \
			$(PYRUNLIBDIR) \
			$(PYRUNSHAREDLIBDIR) \
			$(PYRUNSITEPACKAGESLIBDIR) \
			$(PYRUNINCLUDEDIR)

$(FULLPYTHON):	$(PYTHONDIR) $(PYRUNSOURCEDIR)/$(MODULESSETUP)
	# Rebuild the modules config unconditionally (since the Makefile has
	# to be rebuilt, if the Setup changes)
	$(MAKE) modules $(BUILDDIR)
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Creating Python interpreter ==============================================="
	@$(ECHO) "$(OFF)"
	cd $(PYTHONDIR); \
	$(MAKE); \
	$(MAKE) install

interpreter:	$(FULLPYTHON)

$(PYRUNINCLUDEDIR)/patchlevel.h:	$(FULLPYTHON)
	$(CP_DIR) -f $(FULLSHAREDLIBDIR)/* $(PYRUNSHAREDLIBDIR)
	# Remove test and xx modules
	$(RM) -f $(PYRUNSHAREDLIBDIR)/*_test*
	$(RM) -f $(PYRUNSHAREDLIBDIR)/xx*
	$(RM) -f $(PYRUNSHAREDLIBDIR)/_xx*
	$(CP_DIR) -f $(FULLSITEPACKAGESLIBDIR)/* $(PYRUNSITEPACKAGESLIBDIR)
	$(CP_DIR) -f $(FULLINCLUDEDIR)/* $(PYRUNINCLUDEDIR)

$(PYRUNDIR):	$(BASEDIR)
	mkdir -p $(PYRUNDIR)

$(PYRUNDIR)/makepyrun.py:	$(PYRUNDIR) $(PYRUNSOURCEDIR)/*.py
	$(CP_DIR) -f $(PYRUNSOURCEDIR)/*.py $(PYRUNDIR)
	$(CP_DIR) -f $(PYRUNSOURCEDIR)/freeze-* $(PYRUNDIR)

$(PYRUNDIR)/$(PYRUNPY):	$(FULLPYTHON) $(PYRUNDIR)/makepyrun.py
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Preparing PyRun ==========================================================="
	@$(ECHO) "$(OFF)"
	cd $(PYRUNDIR); \
	unset PYTHONPATH; export PYTHONPATH; \
	export PYTHONHOME=$(FULLINSTALLDIR); \
	unset PYTHONINSPECT; export PYTHONINSPECT; \
	$(FULLPYTHON) makepyrun.py $(PYRUNPY)
	@$(ECHO) "Created $(PYRUNPY)."

prepare:	$(PYRUNDIR)/$(PYRUNPY)

test-makepyrun:
	cd $(PYRUNDIR); \
	unset PYTHONPATH; export PYTHONPATH; \
	export PYTHONHOME=$(FULLINSTALLDIR); \
	unset PYTHONINSPECT; export PYTHONINSPECT; \
	$(FULLPYTHON) makepyrun.py $(PYRUNPY)
	@$(ECHO) "Created $(PYRUNPY)."

$(PYRUNDIR)/$(PYRUN):	$(FULLPYTHON) $(PYRUNDIR)/$(PYRUNPY) $(FREEZEDIR) $(BUILDDIR)
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Creating PyRun ============================================================"
	@$(ECHO) "$(OFF)"
        # Cleanup the PyRun freeze build dir
	cd $(PYRUNDIR); $(RM) -f *.c *.o
        # Run freeze to build pyrun
	cd $(FREEZEDIR); \
	unset PYTHONPATH; export PYTHONPATH; \
	export PYTHONHOME=$(FULLINSTALLDIR); \
	unset PYTHONINSPECT; export PYTHONINSPECT; \
	$(FULLPYTHON) \
		$(PYRUNFREEZEOPTIMIZATION) \
		$(PYRUNFREEZEDEBUGRANGES) \
		freeze.py -d \
		-o $(PYRUNDIR) \
		-r $(PYRUNLIBDIRCODEPREFIX) \
		-r $(PYRUNDIRCODEPREFIX) \
		$(EXCLUDES) \
	        $(PYRUNDIR)/$(PYRUNPY)
	cd $(PYRUNDIR); \
	export LD_RUN_PATH="$(PYRUNRPATH)"; \
	$(MAKE); \
	$(CP) $(PYRUN) $(PYRUN_DEBUG); \
	$(STRIP) $(STRIPOPTIONS) $(PYRUN); \
	$(CP) $(PYRUN) $(PYRUN_STANDARD); \
	if ! test -z "$(UPX)"; then \
	    $(UPX) $(UPXOPTIONS) $(PYRUN); \
	    $(CHMOD) +x $(PYRUN); \
	    ln -sf $(PYRUN) $(PYRUN_UPX); \
	fi

$(BINDIR)/$(PYRUN):	$(PYRUNDIR)/$(PYRUN)
	@$(ECHO) "Installing PyRun to $(BINDIR)"
	cd $(PYRUNDIR); \
	$(CP) $(PYRUN) $(BINDIR); \
	$(CP) $(PYRUN_STANDARD) $(BINDIR); \
	$(CP) $(PYRUN_DEBUG) $(BINDIR); \
	if test -e $(PYRUN_UPX); then $(CP) -d $(PYRUN_UPX) $(BINDIR); fi
	cd $(BINDIR); \
	ln -sf $(PYRUN) $(PYRUN_GENERIC); \
	ln -sf $(PYRUN) $(PYRUN_SYMLINK); \
	ln -sf $(PYRUN) $(PYRUN_SYMLINK_GENERIC)
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Finished =================================================================="
	@$(ECHO) "$(OFF)"
	@$(ECHO) "The eGenix PyRun runtime interpreter is called: $(BINDIR)/$(PYRUN)"
	@$(ECHO) ""

runtime:	$(BINDIR)/$(PYRUN)

build:	clean distribution

build-all:
	@for i in $(PYTHONVERSIONS); do \
	  $(MAKE) build PYTHONFULLVERSION=$$i; $(ECHO) ""; \
	done

### Installation

install-bin:	$(BINDIR)/$(PYRUN)
	if ! test -d $(INSTALLBINDIR); then mkdir -p $(INSTALLBINDIR); fi;
	if test $(INSTALLALLBINARIES); then \
	   echo "Installing all PyRun binaries"; \
	   $(CP) -a 	$(BINDIR)/* $(INSTALLBINDIR); \
	else \
	   echo "Installing standard set of PyRun binaries"; \
	   $(CP) -a	$(BINDIR)/$(PYRUN) \
			$(BINDIR)/$(PYRUN_GENERIC) \
			$(BINDIR)/$(PYRUN_SYMLINK) \
			$(BINDIR)/$(PYRUN_SYMLINK_GENERIC) \
			$(INSTALLBINDIR); \
	fi

install-lib:	$(PYRUNINCLUDEDIR)/patchlevel.h
	if ! test -d $(INSTALLLIBDIR); then mkdir -p $(INSTALLLIBDIR); fi;
	$(CP_DIR) $(PYRUNLIBDIR) $(INSTALLLIBDIR)

install-include:	$(PYRUNINCLUDEDIR)/patchlevel.h
	if ! test -d $(INSTALLINCLUDEDIR); then mkdir -p $(INSTALLINCLUDEDIR); fi;
	$(CP_DIR) $(PYRUNINCLUDEDIR) $(INSTALLINCLUDEDIR)

install:	install-bin install-lib install-include

### Packaging

$(BINARY_DISTRIBUTION_ARCHIVE):	$(BINDIR)/$(PYRUN) $(PYRUNINCLUDEDIR)/patchlevel.h
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Creating PyRun Distribution =============================================="
	@$(ECHO) "$(OFF)"
	$(MAKE) install PREFIX=$(DISTBUILDDIR) \
		PYTHONFULLVERSION=$(PYTHONFULLVERSION)
	mkdir -p $(DISTDIR)
	cd $(DISTBUILDDIR); \
	$(TAR) -c -z -f $@ .
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Finished =================================================================="
	@$(ECHO) "$(OFF)"
	@$(ECHO) "The eGenix PyRun Distribution is called: $(BINARY_DISTRIBUTION_ARCHIVE)"
	@$(ECHO) ""

distribution:	announce-distribution logs
	$(MAKE) $(BINARY_DISTRIBUTION_ARCHIVE) \
		$(LOGREDIR)

all-distributions:
	@for i in $(PYTHONVERSIONS); do \
	  $(MAKE) distribution PYTHONFULLVERSION=$$i; $(ECHO) ""; \
	done

# These targets should not be used for building production
# distributions; it's meant to be used during development, since it runs
# builds in parallel and without PGO

dev-build-distribution:
	@$(ECHO) "Building a dev distribution..."
	$(MAKE) distribution \
		PYTHON_CONFIGURE_OPTIONS="$(PYTHON_DEV_CONFIGURE_OPTIONS)"

dev-build-all-distributions:
	@$(ECHO) "Building dev distributions in parallel..."
	@for i in $(PYTHONVERSIONS); do \
	  ($(MAKE) distribution \
		PYTHONFULLVERSION=$$i \
		PYTHON_CONFIGURE_OPTIONS="$(PYTHON_DEV_CONFIGURE_OPTIONS)" \
		&); \
	done

### Testing

$(TESTDIR)/bin/$(PYRUN):	$(BINARY_DISTRIBUTION_ARCHIVE)
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Installing PyRun for Tests ==============================================="
	@$(ECHO) "$(OFF)"
	$(RM) -rf $(TESTDIR)
	./install-pyrun \
		--log \
		--setuptools-version=latest \
		--pip-version=latest \
		--pyrun-distribution=$(BINARY_DISTRIBUTION_ARCHIVE) \
		$(TESTDIR)
	touch $@

test-install-pyrun:	$(TESTDIR)/bin/$(PYRUN)

test-basic:	$(TESTDIR)/bin/$(PYRUN)
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Running Tests ============================================================="
	@$(ECHO) "$(OFF)"
	@$(ECHO) "--- Testing basic operation --------------------------------------"
	@$(ECHO) ""
	cd $(TESTDIR); bin/pyrun $(PYRUNTESTS)/test_basic.py
	$(CP_DIR) tests $(TESTDIR); cd $(TESTDIR); bin/pyrun $(PYRUNTESTS)/test_cmdline.py
	@$(ECHO) ""
	@$(ECHO) "--- Testing direct execution of commands -------------------------"
	@$(ECHO) ""
	cd $(TESTDIR); bin/pyrun -c "import sys; print(sys.version)"
	cd $(TESTDIR); echo "import sys; print(sys.version)" | bin/pyrun
	cd $(TESTDIR); echo "import sys; print(sys.version)" | bin/pyrun -
	@$(ECHO) ""
	@$(ECHO) "--- Testing module runs ------------------------------------------"
	@$(ECHO) ""
	cd $(TESTDIR); bin/pyrun -m timeit
	@$(ECHO) ""

test-ssl:	$(TESTDIR)/bin/$(PYRUN)
	@$(ECHO) "--- Testing SSL installation  ------------------------------------"
	@$(ECHO) ""
ifdef PYTHON_2_BUILD
	cd $(TESTDIR); export EGENIX_CRYPTO_CONFIRM=1; bin/pip install egenix-pyopenssl
else
	cd $(TESTDIR); bin/pip install -U pip setuptools pyopenssl
endif
	export -n PYRUN_HTTPSVERIFY; cd $(TESTDIR); bin/pyrun $(PYRUNTESTS)/test_ssl.py
	export PYRUN_HTTPSVERIFY=0; cd $(TESTDIR); bin/pyrun $(PYRUNTESTS)/test_ssl.py
	export PYRUN_HTTPSVERIFY=1; cd $(TESTDIR); bin/pyrun $(PYRUNTESTS)/test_ssl.py
	@$(ECHO) ""

ifdef PYTHON_2_BUILD
test-pip:	$(TESTDIR)/bin/$(PYRUN)
	@$(ECHO) "--- Testing pip installation (pure Python) -----------------------"
	@$(ECHO) ""
	cd $(TESTDIR); bin/pip install Genshi
	cd $(TESTDIR); bin/pip install Trac==0.12
	cd $(TESTDIR); bin/pip install requests
	@$(ECHO) ""
	@$(ECHO) "--- Testing pip installation (packages with C extensions) --------"
	@$(ECHO) ""
	cd $(TESTDIR); bin/pip install egenix-mx-base
	cd $(TESTDIR); bin/pip install numpy
	cd $(TESTDIR); bin/pip install lxml
	@$(ECHO) ""
	@$(ECHO) "--- Testing pip installation (heavy weight packages) -------------"
	@$(ECHO) ""
	cd $(TESTDIR); bin/pip install cython
	cd $(TESTDIR); bin/pip install Django
else
test-pip:	$(TESTDIR)/bin/$(PYRUN)
	@$(ECHO) "--- Testing pip installation (pure Python) -----------------------"
	@$(ECHO) ""
	cd $(TESTDIR); bin/pip install requests
	cd $(TESTDIR); bin/pip install Werkzeug
	@$(ECHO) ""
	@$(ECHO) "--- Testing pip installation (packages with C extensions) --------"
	@$(ECHO) ""
	cd $(TESTDIR); bin/pip install flask
	cd $(TESTDIR); bin/pip install numpy
	cd $(TESTDIR); bin/pip install lxml
	@$(ECHO) ""
	@$(ECHO) "--- Testing pip installation (heavy weight packages) -------------"
	@$(ECHO) ""
	cd $(TESTDIR); bin/pip install cython
	cd $(TESTDIR); bin/pip install Django
endif

test-pip-latest:
	$(RM) -rf $(TESTDIR)
	$(MAKE) test-install-pyrun
	@$(ECHO) "--- Upgrading to latest pip --------------------------------------"
	@$(ECHO) ""
	cd $(TESTDIR); bin/pip install -U setuptools
	cd $(TESTDIR); bin/pip install -U pip
	@$(ECHO) ""
	$(MAKE) test-pip

test-distribution:	test-basic test-pip test-pip-latest

test-all-pyruns:
	@for i in $(PYTHONVERSIONS); do \
	  $(MAKE) test-basic \
		PYTHONFULLVERSION=$$i \
		$(LOGREDIR); \
	  $(ECHO) ""; \
	done

test-all-distributions:
	@for i in $(PYTHONVERSIONS); do \
	  $(MAKE) test-distribution \
		PYTHONFULLVERSION=$$i \
		$(LOGREDIR); \
	  $(ECHO) ""; \
	done

### Cleanup

clean:
	$(RM) -rf $(BASEDIR)

clean-test:
	$(RM) -rf $(TESTDIR)

clean-all:
	@for i in $(PYTHONVERSIONS); do \
	  $(ECHO) "Clean up $$i build"; \
	  $(MAKE) clean PYTHONFULLVERSION=$$i; \
	  $(ECHO) ""; \
	done

distclean:	clean
	$(RM) -rf $(DISTDIR) $(TESTDIR) $(BUILDDIR)
	find . \( -name '*~' -or -name '*.bak' \) -delete

distclean-all:
	@for i in $(PYTHONVERSIONS); do \
	  $(ECHO) "Dist clean $$i build"; \
	  $(MAKE) distclean PYTHONFULLVERSION=$$i; \
	  $(ECHO) ""; \
	done

spring-clean:
	$(RM) -rf Python-2.* Python-3.* tmp-* test-pyrun-* build-*

### Misc other targets

create-python-patch:
	@$(ECHO) "Creating patch for $(PYTHONVERSION)"
	cd $(PYTHONDIR); \
	diff -ur \
		-x 'importlib.h' \
		-x 'Setup' \
		$(PYTHONORIGDIFFDIR) . | \
		sed '/Only in .*/d' \
		>  $(PYRUNSOURCEDIR)/$(PYTHONPATCHFILE)

create-all-patches:
	@for i in $(PYTHONVERSIONS); do \
	  $(MAKE) create-python-patch PYTHONFULLVERSION=$$i; $(ECHO) ""; \
	done

print-exported-python-api:	$(BINDIR)/$(PYRUN)
	nm $(BINDIR)/$(PYRUN) | egrep -v ' T _?Py' | sort -k 2

versions:
	echo "PyRun version: $(PACKAGEVERSION)"
	echo "-----------------------------------"
	echo "Python version: $(PYTHONFULLVERSION) ($(PYTHONVERSION) = $(PYTHONMAJORVERSION).$(PYTHONMINORVERSION))"
	echo "PyRun Python version: $(PYRUNFULLVERSION)"
	echo "PyRun platform: $(PLATFORM)"
	echo "PyRun Unicode: $(PYTHONUNICODE)"
	echo "PyRun archive base name: $(ARCHIVE)"
	echo "PyRun binary: $(BINDIR)/$(PYRUN)"
	echo "PyRun SSL dir: $(PYRUN_SSL)"

### Debugging

print-vars:
	@$(foreach V,\
		$(sort $(.VARIABLES)), \
                $(warning $V=$($V)))

print-env:
	env | sort

# rpath test target:
show-rpath:
	echo "Makefile setting:"
	echo "PYRUNRPATH = $(PYRUNRPATH)"
	if [ -e $(BINDIR)/$(PYRUN) ]; then \
	    echo ""; \
	    echo "Binary $(BINDIR)/$(PYRUN):"; \
	    readelf -d $(BINDIR)/$(PYRUN) | grep PATH; \
	fi
