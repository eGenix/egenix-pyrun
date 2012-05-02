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

# Project dir
PWD := $(shell pwd)

# Python versions to use for pyrun
PYTHON_27_VERSION = 2.7.2
PYTHON_26_VERSION = 2.6.7
PYTHON_25_VERSION = 2.5.6

# Python version to use as basis for pyrun
PYTHONFULLVERSION = $(PYTHON_27_VERSION)
#PYTHONFULLVERSION = $(PYTHON_26_VERSION)
#PYTHONFULLVERSION = $(PYTHON_25_VERSION)

# Version & Platform
PYTHONVERSION := $(shell echo $(PYTHONFULLVERSION) | sed 's/\([0-9]\.[0-9]\).*/\1/')
PYRUNFULLVERSION = $(PYTHONFULLVERSION)
PYRUNVERSION = $(PYTHONVERSION)
PLATFORM := $(shell python Runtime/platform.py)

# Name of the resulting pyrun executable
PYRUN_GENERIC = pyrun
PYRUN = $(PYRUN_GENERIC)$(PYRUNVERSION)

# Archive name to create with "make archive"
ARCHIVE = $(PYRUN)-$(PYRUNFULLVERSION)-$(PLATFORM)

# Location of the Python tarball
PYTHONTARBALL = /downloads/egenix-build-environment/Python-$(PYTHONFULLVERSION).tgz
PYTHONSOURCEURL = http://www.python.org/ftp/python/$(PYTHONFULLVERSION)/Python-$(PYTHONFULLVERSION).tgz
WGET = wget

# Directories
PYTHONDIR = $(PWD)/Python-$(PYTHONFULLVERSION)
PYRUNDIR = $(PWD)/Runtime

# Name of the freeze template and executable
PYRUNPY = $(PYRUN).py

# Name of the special eGenix PyRun Modules/Setup file
MODULESSETUP = Setup.PyRun-$(PYTHONVERSION)

# Name of the pyrun Python patch file
PYTHONPATCHFILE = Python-$(PYTHONVERSION).patch

# Name of the temporary installation target dir
TMPINSTALLDIR = $(PWD)/tmp-$(PYTHONVERSION)
TMPPYTHON = $(TMPINSTALLDIR)/bin/python$(PYTHONVERSION)
TMPLIBDIR = $(TMPINSTALLDIR)/lib/python$(PYRUNVERSION)
TMPSHAREDLIBDIR = $(TMPLIBDIR)/lib-dynload
TMPINCLUDEDIR = $(TMPINSTALLDIR)/include/python$(PYRUNVERSION)

# Target dir of shared modules
LIBDIR = $(PWD)/lib
PYRUNLIBDIR = $(LIBDIR)/python$(PYRUNVERSION)

# Target dir for include files
INCLUDEDIR = $(PWD)/include
PYRUNINCLUDEDIR = $(INCLUDEDIR)/python$(PYRUNVERSION)

# Installation directories
PREFIX = /usr/local
INSTALLBINDIR = $(PREFIX)/bin
INSTALLLIBDIR = $(PREFIX)/lib
INSTALLINCLUDEDIR = $(PREFIX)/include

# Packages and modules to exclude from the runtime
EXCLUDES = 

# Tools
TAR = tar
# Note: MAKE is a pre-defined variable in GNU make
RM = /bin/rm
STRIP = strip

# Python configure options
PYTHON_CONFIGURE_OPTIONS = ""
PYTHON_25_BUILD := $(shell test PYTHONVERSION = "2.5" && echo "1")
PYTHON_26_BUILD := $(shell test PYTHONVERSION = "2.6" && echo "1")
PYTHON_27_BUILD := $(shell test PYTHONVERSION = "2.7" && echo "1")

# Build platform
MACOSX_PLATFORM := $(shell test "`uname -s`" = "Darwin" && echo "1")
MACOSX_PPC_PLATFORM := $(shell test "`uname -s -p`" = "Darwin powerpc" && echo "1")
MACOSX_INTEL_PLATFORM := $(shell test "`uname -s -p`" = "Darwin i386" && echo "1")

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

# Stripping the executable
# 
# Note: strip on Macs strips too much information from the executable
# per default, rendering the resulting executable unusable for dynamic
# linking. See #792. Use -S to only strip the debug information like
# on Linux
STRIPOPTIONS = -S

### Generic targets

all:	pyrun

pyrun:	config interpreter runtime

### Build process

$(PYTHONDIR):
	echo "=== Setting up the Python sources ===================================================="
	$(RM) -rf $(PYTHONDIR)
	if test -z $(PYTHONTARBALL) || ! test -e $(PYTHONTARBALL); then \
	    echo "Downloading and extracting $(PYTHONSOURCEURL)."; \
	    $(WGET) -O - $(PYTHONSOURCEURL) | tar xz ; \
	else \
	    echo "Extracting local copy $(PYTHONTARBALL)."; \
	    $(TAR) xfz $(PYTHONTARBALL) ; \
	fi
        # Apply Python patches needed for pyrun
	cd $(PYTHONDIR); \
	patch -p0 -F10 < ../Runtime/$(PYTHONPATCHFILE)

sources: $(PYTHONDIR)

# Note: The dependency is on the Python patchlevel.h file, not the
# source directory.  This is to avoid unnecessary rebuilds in case the
# source directory changes for whatever reason during builds.

$(PYTHONDIR)/Include/patchlevel.h:
	$(MAKE) $(PYTHONDIR)

$(PYTHONDIR)/pyconfig.h:	$(PYTHONDIR)/Include/patchlevel.h
	echo "=== Configuring Python ==============================================================="
	cd $(PYTHONDIR); \
	./configure \
		--prefix=$(TMPINSTALLDIR) \
		--exec-prefix=$(TMPINSTALLDIR) \
		$(PYTHON_CONFIGURE_OPTIONS)
	touch $@

config: $(PYTHONDIR)/pyconfig.h $(PYRUNDIR)/$(MODULESSETUP)
        # Create install dir structure
	if test -d $(TMPINSTALLDIR); then $(RM) -rf $(TMPINSTALLDIR); fi
	mkdir -p $(TMPINSTALLDIR) $(TMPINSTALLDIR)/lib $(TMPINSTALLDIR)/bin $(TMPINSTALLDIR)/include
	if test -d $(PYRUNLIBDIR); then $(RM) -rf $(PYRUNLIBDIR); fi
	mkdir -p $(PYRUNLIBDIR)
        # Install the custom Modules/Setup file
	if test "$(MACOSX_PLATFORM)"; then \
		sed 	-e 's/#@MACOSX@//' \
			$(PYRUNDIR)/$(MODULESSETUP) > $(PYTHONDIR)/Modules/Setup; \
	else \
		cp $(PYRUNDIR)/$(MODULESSETUP) $(PYTHONDIR)/Modules/Setup; \
	fi;
        # Recreate the Makefile after the above changes
	cd $(PYTHONDIR); \
	$(RM) Makefile; \
	$(MAKE) -f Makefile.pre Makefile

$(TMPPYTHON):	$(PYTHONDIR)/pyconfig.h $(PYRUNDIR)/$(MODULESSETUP)
	echo "=== Creating Python interpreter ======================================================"
	$(MAKE) config
	cd $(PYTHONDIR); \
	$(MAKE); \
	$(MAKE) install; \
	if ! test -d $(PYRUNLIBDIR); then mkdir -p $(PYRUNLIBDIR); fi; \
	cp -vaf	$(TMPSHAREDLIBDIR)/* $(PYRUNLIBDIR); \
	if ! test -d $(PYRUNINCLUDEDIR); then mkdir -p $(PYRUNINCLUDEDIR); fi; \
	cp -vaf $(TMPINCLUDEDIR)/* $(PYRUNINCLUDEDIR)
	touch $@ $(PYTHONDIR)

interpreter:	$(TMPPYTHON)

Runtime/$(PYRUNPY):	$(TMPPYTHON) Runtime/makepyrun.py Runtime/pyrun_template.py Runtime/pyrun_config_template.py
	echo "=== Preparing PyRun =================================================================="
	cd Runtime; \
	unset PYTHONPATH; export PYTHONPATH; \
	export PYTHONHOME=$(TMPINSTALLDIR); \
	unset PYTHONINSPECT; export PYTHONINSPECT; \
	$(TMPPYTHON) makepyrun.py $(PYRUNPY)
	echo "Created $(PYRUNPY)."
	touch $@

prepare:	Runtime/$(PYRUNPY)

test-makepyrun:
	cd Runtime; \
	unset PYTHONPATH; export PYTHONPATH; \
	export PYTHONHOME=$(TMPINSTALLDIR); \
	unset PYTHONINSPECT; export PYTHONINSPECT; \
	$(TMPPYTHON) makepyrun.py $(PYRUNPY)
	echo "Created $(PYRUNPY)."

$(PYRUN):	Runtime/$(PYRUNPY)
	echo "=== Creating PyRun ==================================================================="
        # Cleanup the PyRun freeze build dir
	cd Runtime; $(RM) -f *.c *.o
        # Run freeze to build pyrun
	cd Runtime/freeze; \
	unset PYTHONPATH; export PYTHONPATH; \
	export PYTHONHOME=$(TMPINSTALLDIR); \
	unset PYTHONINSPECT; export PYTHONINSPECT; \
	$(TMPPYTHON) -O freeze.py -d \
		-o $(PYRUNDIR) \
		$(EXCLUDES) \
	        $(PYRUNDIR)/$(PYRUNPY)
	cd $(PYRUNDIR); \
	$(MAKE); \
	cp $(PYRUN) $(PYRUN)-debug; \
	$(STRIP) $(STRIPOPTIONS) $(PYRUN)
	cp $(PYRUNDIR)/$(PYRUN) .
	cp $(PYRUNDIR)/$(PYRUN)-debug .
	echo "=== Finished ========================================================================="
	@echo
	@echo "The eGenix PyRun runtime interpreter is called: ./$(PYRUN)"
	@echo
	touch $@

runtime:	$(PYRUN)

### Installation

install-bin:	$(PYRUN)
	if ! test -d $(INSTALLBINDIR); then mkdir -p $(INSTALLBINDIR); fi;
	cp $(PYRUN) $(INSTALLBINDIR)
	ln -sf $(PYRUN) $(INSTALLBINDIR)/$(PYRUN_GENERIC)

install-lib:
	if ! test -d $(INSTALLLIBDIR); then mkdir -p $(INSTALLLIBDIR); fi;
	cp -r $(PYRUNLIBDIR) $(INSTALLLIBDIR)

install-include:
	if ! test -d $(INSTALLINCLUDEDIR); then mkdir -p $(INSTALLINCLUDEDIR); fi;
	cp -r $(PYRUNINCLUDEDIR) $(INSTALLINCLUDEDIR)

install:	install-bin install-lib install-include

### Packaging

$(PYRUN).gz:	$(PYRUN)
	gzip -9c $(PYRUN) > $(PYRUN).gz

archive:	$(PYRUN).gz
	cp $(PYRUN).gz $(ARCHIVE).gz

### Cleanup

clean-runtime:
	$(RM) -rf \
		$(PYRUNDIR)/*.c \
		$(PYRUNDIR)/*.o \
		$(PYRUNDIR)/Makefile \
		$(PYRUNDIR)/$(PYRUN) \
		$(PYRUNDIR)/$(PYRUN)-debug \
		$(PYRUNDIR)/$(PYRUNPY); \
	true

clean:	clean-runtime
	$(RM) -rf \
		$(TMPINSTALLDIR) \
		$(PYRUNLIBDIR); \
	true

distclean:	clean
	$(RM) -rf \
		$(PYRUN) \
		$(PYRUN)-debug \
		$(PYTHONDIR) \
	true

### Special build targets

build-all: build-pyrun25 build-pyrun26 build-pyrun27

build-pyrun27:
	$(MAKE) clean pyrun PYTHONFULLVERSION=$(PYTHON_27_VERSION)

build-pyrun26:
	$(MAKE) clean pyrun PYTHONFULLVERSION=$(PYTHON_26_VERSION)

build-pyrun25:
	$(MAKE) clean pyrun PYTHONFULLVERSION=$(PYTHON_25_VERSION)

