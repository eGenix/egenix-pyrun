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
# Note: When changing the versions here, also update them in the product
# Makefile.
#
PYTHON_310_VERSION = 3.10.11
PYTHON_39_VERSION = 3.9.16
PYTHON_38_VERSION = 3.8.16
PYTHON_37_VERSION = 3.7.16
PYTHON_36_VERSION = 3.6.15
PYTHON_27_VERSION = 2.7.18

# Python version to use as basis for pyrun
PYTHONFULLVERSION = $(PYTHON_310_VERSION)
#PYTHONFULLVERSION = $(PYTHON_39_VERSION)
#PYTHONFULLVERSION = $(PYTHON_38_VERSION)
#PYTHONFULLVERSION = $(PYTHON_37_VERSION)
#PYTHONFULLVERSION = $(PYTHON_36_VERSION)
#PYTHONFULLVERSION = $(PYTHON_27_VERSION)

# All target versions
PYTHONVERSIONS = \
	$(PYTHON_27_VERSION) \
	$(PYTHON_36_VERSION) \
	$(PYTHON_37_VERSION) \
	$(PYTHON_38_VERSION) \
	$(PYTHON_39_VERSION) \
	$(PYTHON_310_VERSION)

# Python Unicode version
PYTHONUNICODE = ucs2

# Python 3 ABI flags (see PEP 3149)
#
# These should probably be determined by running a standard Python 3
# and checking sys.abiflags. Hardcoding them here for now, since they
# rarely change.
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
		-x pip

# Package details (used for distributions and normally passed in via
# the product Makefile)
PACKAGENAME = egenix-pyrun

# Package version; note that you have to keep this in sync with
# Runtime/makepyrun.py
PACKAGEVERSION = 2.4.0
#PACKAGEVERSION = $(shell cd Runtime; python -c "from makepyrun import __version__; print __version__")

# OpenSSL installation to compile and link against. If an environment
# variable SSL is given we use that.  Otherwise, We check a few custom
# locations which possibly more recent versions before going to the standard
# system paths.  /usr/local is common on Linux, /usr/contrib on HP-UX,
# /usr/sfw on Solaris/OpenIndiana, fallback is /usr.
PYRUN_SSL = $(shell if ( test -n "$(SSL)" ); then echo $(SSL); \
		    elif ( test -e /usr/include/openssl/ssl.h ); then echo /usr; \
		    elif ( test -e /usr/local/ssl/include/openssl/ssl.h ); then echo /usr/local/ssl; \
		    elif ( test -e /usr/contrib/ssl/include/openssl/ssl.h ); then echo /usr/contrib/ssl; \
		    elif ( test -e /usr/sfw/include/openssl/ssl.h ); then echo /usr/sfw; \
		    else echo /usr; \
		    fi)

### Runtime build parameters

# Project dir
PWD := $(shell pwd)

# Version & Platform
PYTHONVERSION := $(shell echo $(PYTHONFULLVERSION) | sed 's/\([0-9]\.[0-9]\+\).*/\1/')
PYTHONMAJORVERSION := $(shell echo $(PYTHONFULLVERSION) | sed 's/\([0-9]\+\)\..*/\1/')
PYTHONMINORVERSION := $(shell echo $(PYTHONFULLVERSION) | sed 's/[0-9]\.\([0-9]\+\)\..*/\1/')
PYRUNFULLVERSION = $(PYTHONFULLVERSION)
PYRUNVERSION = $(PYTHONVERSION)
PLATFORM := $(shell python -c "from distutils.util import get_platform; print get_platform()")

# Python build flags
PYTHON_2_BUILD := $(shell test "$(PYTHONMAJORVERSION)" = "2" && echo "1")
PYTHON_27_BUILD := $(shell test "$(PYTHONVERSION)" = "2.7" && echo "1")
PYTHON_3_BUILD := $(shell test "$(PYTHONMAJORVERSION)" = "3" && echo "1")
PYTHON_36_BUILD := $(shell test "$(PYTHONVERSION)" = "3.6" && echo "1")
PYTHON_37_BUILD := $(shell test "$(PYTHONVERSION)" = "3.7" && echo "1")
PYTHON_37_OR_EARLIER_BUILD := $(shell test $(PYTHONMAJORVERSION) -eq 3 && test $(PYTHONMINORVERSION) -lt 8 && echo "1")
PYTHON_38_BUILD := $(shell test "$(PYTHONVERSION)" = "3.8" && echo "1")
PYTHON_39_BUILD := $(shell test "$(PYTHONVERSION)" = "3.9" && echo "1")
PYTHON_310_BUILD := $(shell test "$(PYTHONVERSION)" = "3.10" && echo "1")

# Special Python environment setups
ifdef PYTHON_3_BUILD
 # We support Python 3.5+ only, which no longer has different versions
 # for Unicode. Since PYTHONUNICODE is used in a lot of places, we
 # simply assign a generic term to it for Python 3.
 PYTHONUNICODE := ucs4
endif

# Name of the resulting pyrun executable
PYRUN_GENERIC = pyrun
PYRUN = $(PYRUN_GENERIC)$(PYRUNVERSION)
PYRUN_DEBUG = $(PYRUN)-debug

# Symlinks to create for better Python compatibility
ifdef PYTHON_2_BUILD
 PYRUN_SYMLINK_GENERIC = python
 PYRUN_SYMLINK = python$(PYRUNVERSION)
else
 PYRUN_SYMLINK_GENERIC = python3
 PYRUN_SYMLINK = python$(PYRUNVERSION)
endif

# Archive name to create with "make archive"
ARCHIVE = $(PYRUN)-$(PYRUNFULLVERSION)-$(PLATFORM)

# Location of the Python tarball
PYTHONTARBALL = /downloads/egenix-build-environment/Python-$(PYTHONFULLVERSION).tgz
PYTHONSOURCEURL = https://www.python.org/ftp/python/$(PYTHONFULLVERSION)/Python-$(PYTHONFULLVERSION).tgz

# Directories
PYTHONORIGDIR = $(PWD)/Python-$(PYTHONFULLVERSION)
PYTHONDIR = $(PWD)/Python-$(PYTHONFULLVERSION)-$(PYTHONUNICODE)
PYRUNDIR = $(PWD)/Runtime
ifdef PYTHON_2_BUILD
 FREEZEDIR = Runtime/freeze-2
else
 FREEZEDIR = Runtime/freeze-3
endif

# Freeze optimization settings; the freeze.py script is run with these
# Python optimization settings, which affect the way the stdlib modules are
# compiled.
PYRUNFREEZEOPTIMIZATION = -O

# Name of the freeze template and executable
PYRUNPY = $(PYRUN).py

# Name of the special eGenix PyRun Modules/Setup file
MODULESSETUP = Setup.PyRun-$(PYTHONVERSION)

# Name of the pyrun Python patch file
PYTHONPATCHFILE = Python-$(PYTHONVERSION).patch

# Name of the temporary installation target dir
TMPINSTALLDIR = $(PWD)/tmp-$(PYTHONVERSION)-$(PYTHONUNICODE)
TMPPYTHON = $(TMPINSTALLDIR)/bin/python$(PYTHONVERSION)
TMPLIBDIR = $(TMPINSTALLDIR)/lib/python$(PYRUNVERSION)
TMPSHAREDLIBDIR = $(TMPLIBDIR)/lib-dynload
TMPSITEPACKAGESLIBDIR = $(TMPLIBDIR)/site-packages
ifdef PYTHON_2_BUILD
 # Python 2.x did not have ABI dirs
 TMPINCLUDEDIR = $(TMPINSTALLDIR)/include/python$(PYRUNVERSION)
else ifdef PYTHON_37_OR_EARLIER_BUILD
 # Python 3.x - 3.7 put the include files into an ABI specific dir
 TMPINCLUDEDIR = $(TMPINSTALLDIR)/include/python$(PYRUNVERSION)$(PYTHONABI)
else
 # Python 3.8 returned to the non-ABI dir
 TMPINCLUDEDIR = $(TMPINSTALLDIR)/include/python$(PYRUNVERSION)
endif

# Build dir
BUILDDIR = $(PWD)/build-$(PYTHONVERSION)-$(PYTHONUNICODE)

# Path prefix to use in byte code files embedded into the frozen pyrun
# binary instead of the build time one
PYRUNLIBDIRCODEPREFIX = "$(TMPLIBDIR)=<pyrun>"
PYRUNDIRCODEPREFIX = "$(PYRUNDIR)=<pyrun>"

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
PYRUNORIGIN = \$$ORIGIN
PYRUNRPATH := $(PYRUNORIGIN):$(PYRUNORIGIN)/../lib:$(PYRUNORIGIN)/../lib/python$(PYRUNVERSION)/site-packages/OpenSSL

# rpath test target:
show-rpath:
	echo "Makefile setting:"
	echo "PYRUNRPATH = $(PYRUNRPATH)"
	if [ -e $(BINDIR)/$(PYRUN) ]; then \
	    echo ""; \
	    echo "Binary $(BINDIR)/$(PYRUN):"; \
	    readelf -d $(BINDIR)/$(PYRUN) | grep PATH; \
	fi

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

# Test directory
TESTDIR = $(PWD)/test-$(PYTHONVERSION)-$(PYTHONUNICODE)

# Compiler optimization settings
OPT = -g -O3 -Wall -Wstrict-prototypes
export OPT

# Python configure options
#PYTHON_CONFIGURE_OPTIONS = ""
PYTHON_CONFIGURE_OPTIONS = "--enable-optimizations"

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
CP = cp
CP_DIR = $(CP) -pR
WGET = wget
TPUT = tput
ECHO = /bin/echo -e 

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
		Runtime/makepyrun.py

### Build process

$(PYTHONORIGDIR):
	if test -z $(PYTHONTARBALL) || ! test -e $(PYTHONTARBALL); then \
	    $(ECHO) "Downloading and extracting $(PYTHONSOURCEURL)."; \
	    $(WGET) -O - $(PYTHONSOURCEURL) | tar xz ; \
	else \
	    $(ECHO) "Extracting local copy $(PYTHONTARBALL)."; \
	    $(TAR) xfz $(PYTHONTARBALL) ; \
	fi

python-orig:	$(PYTHONORIGDIR)

$(PYTHONDIR):
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Setting up the Python sources ============================================="
	@$(ECHO) "$(OFF)"
	$(RM) -rf $(PYTHONDIR)
	$(MAKE) $(PYTHONORIGDIR)
        # Move source dir to $(PYTHONDIR)
	mv $(PYTHONORIGDIR) $(PYTHONDIR)
        # Apply Python patches needed for pyrun
	cd $(PYTHONDIR); \
	patch -p0 -F10 < ../Runtime/$(PYTHONPATCHFILE)

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
		--prefix=$(TMPINSTALLDIR) \
		--exec-prefix=$(TMPINSTALLDIR) \
		--libdir=$(TMPINSTALLDIR)/lib \
		--enable-unicode=$(PYTHONUNICODE) \
		$(PYTHON_CONFIGURE_OPTIONS)
	touch $@
else
$(PYTHONDIR)/pyconfig.h:	$(PYTHONDIR)/Include/patchlevel.h
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Configuring Python ========================================================"
	@$(ECHO) "$(OFF)"
	cd $(PYTHONDIR); \
	CONFIG_SITE="" \
	./configure \
		--prefix=$(TMPINSTALLDIR) \
		--exec-prefix=$(TMPINSTALLDIR) \
		--libdir=$(TMPINSTALLDIR)/lib \
		--without-ensurepip \
		$(PYTHON_CONFIGURE_OPTIONS)
	touch $@
endif

config: $(PYTHONDIR)/pyconfig.h $(PYRUNDIR)/$(MODULESSETUP)
        # Create tmp install dir structure
	if test -d $(TMPINSTALLDIR); then $(RM) -rf $(TMPINSTALLDIR); fi
	mkdir -p $(TMPINSTALLDIR) $(TMPINSTALLDIR)/lib $(TMPINSTALLDIR)/bin $(TMPINSTALLDIR)/include
        # Create build dir structure
	if test -d $(BUILDDIR); then $(RM) -rf $(BUILDDIR); fi
	$(MAKE) $(BUILDDIR)
        # Install the custom Modules/Setup file
	if test "$(MACOSX_PLATFORM)"; then \
		sed 	-e 's/# @if macosx: *//' \
			$(PYRUNDIR)/$(MODULESSETUP) > $(PYTHONDIR)/Modules/Setup; \
	elif test "$(FREEBSD_PLATFORM)"; then \
		sed 	-e 's/# @if freebsd: *//' \
			$(PYRUNDIR)/$(MODULESSETUP) > $(PYTHONDIR)/Modules/Setup; \
	else \
		sed 	-e 's/# @if not macosx: *//' \
			-e 's/# @if not freebsd: *//' \
			$(PYRUNDIR)/$(MODULESSETUP) > $(PYTHONDIR)/Modules/Setup; \
	fi;
        # Recreate the Makefile after the above changes
	cd $(PYTHONDIR); \
	$(RM) Makefile; \
	$(MAKE) -f Makefile.pre Makefile

$(TMPPYTHON):	$(PYTHONDIR)/pyconfig.h $(PYRUNDIR)/$(MODULESSETUP)
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Creating Python interpreter ==============================================="
	@$(ECHO) "$(OFF)"
	$(MAKE) config
	cd $(PYTHONDIR); \
	export SSL="$(PYRUN_SSL)"; \
	$(MAKE); \
	$(MAKE) install; \
	if ! test -d $(PYRUNSHAREDLIBDIR); then mkdir -p $(PYRUNSHAREDLIBDIR); fi; \
	$(CP_DIR) -vf $(TMPSHAREDLIBDIR)/* $(PYRUNSHAREDLIBDIR); \
	if ! test -d $(PYRUNSITEPACKAGESLIBDIR); then mkdir -p $(PYRUNSITEPACKAGESLIBDIR); fi; \
	$(CP_DIR) -vf $(TMPSITEPACKAGESLIBDIR)/* $(PYRUNSITEPACKAGESLIBDIR); \
	if ! test -d $(PYRUNINCLUDEDIR); then mkdir -p $(PYRUNINCLUDEDIR); fi; \
	$(CP_DIR) -vf $(TMPINCLUDEDIR)/* $(PYRUNINCLUDEDIR)
	touch $@ $(PYTHONDIR)

interpreter:	$(TMPPYTHON)

Runtime/$(PYRUNPY):	$(TMPPYTHON) Runtime/makepyrun.py Runtime/pyrun_template.py Runtime/pyrun_config_template.py Runtime/pyrun_grammar_template.py
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Preparing PyRun ==========================================================="
	@$(ECHO) "$(OFF)"
	cd Runtime; \
	unset PYTHONPATH; export PYTHONPATH; \
	export PYTHONHOME=$(TMPINSTALLDIR); \
	unset PYTHONINSPECT; export PYTHONINSPECT; \
	$(TMPPYTHON) makepyrun.py $(PYRUNPY)
	@$(ECHO) "Created $(PYRUNPY)."
	touch $@

prepare:	Runtime/$(PYRUNPY)

test-makepyrun:
	cd Runtime; \
	unset PYTHONPATH; export PYTHONPATH; \
	export PYTHONHOME=$(TMPINSTALLDIR); \
	unset PYTHONINSPECT; export PYTHONINSPECT; \
	$(TMPPYTHON) makepyrun.py $(PYRUNPY)
	@$(ECHO) "Created $(PYRUNPY)."

$(BUILDDIR):
	mkdir -p	$(BUILDDIR) \
			$(BINDIR) \
			$(PYRUNLIBDIR) \
			$(PYRUNSHAREDLIBDIR) \
			$(PYRUNSITEPACKAGESLIBDIR) \
			$(PYRUNINCLUDEDIR)

$(BINDIR)/$(PYRUN):	Runtime/$(PYRUNPY) $(BUILDDIR)
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Creating PyRun ============================================================"
	@$(ECHO) "$(OFF)"
        # Cleanup the PyRun freeze build dir
	cd Runtime; $(RM) -f *.c *.o
        # Run freeze to build pyrun
	cd $(FREEZEDIR); \
	unset PYTHONPATH; export PYTHONPATH; \
	export PYTHONHOME=$(TMPINSTALLDIR); \
	unset PYTHONINSPECT; export PYTHONINSPECT; \
	$(TMPPYTHON) $(PYRUNFREEZEOPTIMIZATION) \
		freeze.py -d \
		-o $(PYRUNDIR) \
		-r $(PYRUNLIBDIRCODEPREFIX) \
		-r $(PYRUNDIRCODEPREFIX) \
		$(EXCLUDES) \
	        $(PYRUNDIR)/$(PYRUNPY)
	cd $(PYRUNDIR); \
	export LD_RUN_PATH="$(PYRUNRPATH)"; \
	export SSL="$(PYRUN_SSL)"; \
	$(MAKE); \
	$(CP) $(PYRUN) $(PYRUN_DEBUG); \
	$(STRIP) $(STRIPOPTIONS) $(PYRUN)
	$(CP) $(PYRUNDIR)/$(PYRUN) $(BINDIR)
	$(CP) $(PYRUNDIR)/$(PYRUN_DEBUG) $(BINDIR)
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Finished =================================================================="
	@$(ECHO) "$(OFF)"
	@$(ECHO) "The eGenix PyRun runtime interpreter is called: $(BINDIR)/$(PYRUN)"
	@$(ECHO) ""
	touch $@

runtime:	$(BINDIR)/$(PYRUN)

build:	clean distribution

build-all:
	@for i in $(PYTHONVERSIONS); do \
	  $(MAKE) build PYTHONFULLVERSION=$$i; $(ECHO) ""; \
	done

### Installation

install-bin:	$(BINDIR)/$(PYRUN)
	if ! test -d $(INSTALLBINDIR); then mkdir -p $(INSTALLBINDIR); fi;
	$(CP) $(BINDIR)/$(PYRUN) $(INSTALLBINDIR)
	$(CP) $(BINDIR)/$(PYRUN_DEBUG) $(INSTALLBINDIR)
	cd $(INSTALLBINDIR); \
	ln -sf $(PYRUN) $(PYRUN_GENERIC); \
	ln -sf $(PYRUN) $(PYRUN_SYMLINK); \
	ln -sf $(PYRUN) $(PYRUN_SYMLINK_GENERIC)

install-lib:
	if ! test -d $(INSTALLLIBDIR); then mkdir -p $(INSTALLLIBDIR); fi;
	$(CP_DIR) $(PYRUNLIBDIR) $(INSTALLLIBDIR)

install-include:
	if ! test -d $(INSTALLINCLUDEDIR); then mkdir -p $(INSTALLINCLUDEDIR); fi;
	$(CP_DIR) $(PYRUNINCLUDEDIR) $(INSTALLINCLUDEDIR)

install:	install-bin install-lib install-include

### Packaging

$(BINARY_DISTRIBUTION_ARCHIVE):	$(BINDIR)/$(PYRUN)
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Creating PyRun Distribution =============================================="
	@$(ECHO) "$(OFF)"
	$(MAKE) install PREFIX=$(BUILDDIR)/dist \
		PYTHONFULLVERSION=$(PYTHONFULLVERSION)
	mkdir -p $(DISTDIR)
	cd $(BUILDDIR)/dist; \
	$(TAR) -c -z -f $@ .
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Finished =================================================================="
	@$(ECHO) "$(OFF)"
	@$(ECHO) "The eGenix PyRun Distribution is called: $(BINARY_DISTRIBUTION_ARCHIVE)"
	@$(ECHO) ""
	touch $@

distribution:	announce-distribution logs
	$(MAKE) $(BINARY_DISTRIBUTION_ARCHIVE) \
		$(LOGREDIR)

all-distributions:
	@for i in $(PYTHONVERSIONS); do \
	  $(MAKE) distribution PYTHONFULLVERSION=$$i; $(ECHO) ""; \
	done

### Testing

$(TESTDIR)/bin/$(PYRUN):	$(BINARY_DISTRIBUTION_ARCHIVE)
	@$(ECHO) "$(BOLD)"
	@$(ECHO) "=== Installing PyRun for Tests ==============================================="
	@$(ECHO) "$(OFF)"
	$(RM) -rf $(TESTDIR)
	./install-pyrun \
		--log \
		--debug \
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
	cd $(TESTDIR); bin/pyrun ../test.py
	cp -ar Tests $(TESTDIR); cd $(TESTDIR); bin/pyrun ../testcmdline.py
	cd $(TESTDIR); bin/pyrun -c "import sys; print(sys.version)"
	cd $(TESTDIR); echo "import sys; print(sys.version)" | bin/pyrun
	cd $(TESTDIR); echo "import sys; print(sys.version)" | bin/pyrun -
	@$(ECHO) ""
	@$(ECHO) "--- Testing module imports ---------------------------------------"
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
	export -n PYRUN_HTTPSVERIFY; cd $(TESTDIR); bin/pyrun ../test_ssl.py
	export PYRUN_HTTPSVERIFY=0; cd $(TESTDIR); bin/pyrun ../test_ssl.py
	export PYRUN_HTTPSVERIFY=1; cd $(TESTDIR); bin/pyrun ../test_ssl.py
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
	  $(MAKE) test-basic PYTHONFULLVERSION=$$i; $(ECHO) ""; \
	done

test-all-distributions:
	@for i in $(PYTHONVERSIONS); do \
	  $(MAKE) test-distribution PYTHONFULLVERSION=$$i; $(ECHO) ""; \
	done

### Cleanup

clean-runtime:
	$(RM) -rf \
		$(PYRUNDIR)/*.c \
		$(PYRUNDIR)/*.o \
		$(PYRUNDIR)/Makefile \
		$(PYRUNDIR)/__pycache__ \
		$(PYRUNDIR)/$(PYRUN) \
		$(PYRUNDIR)/$(PYRUN_DEBUG) \
		$(PYRUNDIR)/$(PYRUNPY); \
	true

clean:	clean-runtime
	$(RM) -rf \
		$(TMPINSTALLDIR) \
		$(BUILDDIR) \
		$(TESTDIR) \
		$(PYRUNLIBDIR); \
	true

clean-all:
	@for i in $(PYTHONVERSIONS); do \
	  $(ECHO) "Clean up $$i build"; \
	  $(MAKE) clean PYTHONFULLVERSION=$$i; \
	  $(ECHO) ""; \
	done

distclean:	clean
	$(RM) -rf \
		$(DISTDIR) \
		$(PYTHONORIGDIR) \
		$(PYTHONDIR) \
	true

distclean-all:
	@for i in $(PYTHONVERSIONS); do \
	  $(ECHO) "Dist clean $$i build"; \
	  $(MAKE) distclean PYTHONFULLVERSION=$$i; \
	  $(ECHO) ""; \
	done

spring-clean:
	$(RM) -rf Python-2.* Python-3.* tmp-* test-pyrun-* build-*

### Misc other targets

create-python-patch:	$(PYTHONORIGDIR)
	@$(ECHO) "Creating patch for $(PYTHONVERSION)"
	cd $(PYTHONDIR); \
	diff -ur \
		-x 'importlib.h' \
		-x 'Setup' \
		$(PYTHONORIGDIR) . | sed '/Only in .*/d' \
		>  ../Runtime/$(PYTHONPATCHFILE)

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
