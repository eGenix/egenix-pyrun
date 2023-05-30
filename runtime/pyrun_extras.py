""" eGenix PyRun Extras

    This module can be used to have pyrun include custom other modules
    and packages.

    NOTE: Only pure Python modules/packages may be referenced, since
    pyrun wouldn't be able to include C extensions in the runtime due
    to missing information about how to build them.

"""
# Example:
#
# Include mymodule and all modules referenced by it.
#import mymodule
