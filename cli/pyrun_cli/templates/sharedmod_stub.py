# Shared module stub for {so_file}
#
# This Python module will replaces the shared module file inside ZIP app
# packages and redirects the import to the file living next to the pyrun
# binary.
#
# After import, the shared module replaces this module, so there should
# be no compatibility problems (so he says ;-)).
#
# Part of eGenix PyRun. See https://pyrun.org/ for details.
#
# Written by Marc-Andre Lemburg.
# Copyright (c) 2024, eGenix.com Software GmbH; mailto:info@egenix.com
# License: Apache-2.0
#
def _load_shared_mod(absmodname, so_file):
    import sys
    import os
    from importlib import machinery, util
    absmodname = __name__
    so_dir = os.path.split(sys.executable)[0]
    so_path = os.path.join(so_dir, so_file)
    loader = machinery.ExtensionFileLoader(absmodname, so_path)
    spec = util.spec_from_loader(absmodname, loader)
    module = loader.create_module(spec)
    loader.exec_module(module)
    sys.modules[absmodname] = module
    globals().update(module.__dict__)
_load_shared_mod(__name__, '{so_file}')
del _load_shared_mod
