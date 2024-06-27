#!/usr/bin/env python3
"""
    pyrun_cli.main - CLI entry point

    Written by Marc-Andre Lemburg.
    Copyright (c) 2024, eGenix.com Software GmbH; mailto:info@egenix.com
    License: Apache-2.0

"""
import sys
from pyrun_cli import entry_point

###

if __name__ == '__main__':
    entry_point(sys.argv)
