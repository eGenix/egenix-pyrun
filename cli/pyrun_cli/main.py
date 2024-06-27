#!/usr/bin/env python3
"""
    pyrun_cli.main - CLI entry point

    Written by Marc-Andre Lemburg.
    Copyright (c) 2024, eGenix.com Software GmbH; mailto:info@egenix.com
    License: Apache-2.0

"""
import sys
import argparse
import textwrap

### Globals

### Helpers

_commands = set()

def command(method):

    """ Decorator to declare a command method.

    """
    _commands.add(method.__name__)
    return method

###

class PyRunCLI:

    APP_NAME = 'eGenix PyRun CLI'

    APP_DESCRIPTION = textwrap.dedent("""
    An easy to use interface to installing, using and running eGenix PyRun.
    """).strip()

    APP_EPILOG = textwrap.dedent("""
    Enjoy !
    """).strip()

    # Commands method dictionary; initialized in .__init__()
    commands = None

    def __init__(self):
        self.commands = _commands.copy()

    def parse_argv(self, argv):
        # Command parser
        main_parser = argparse.ArgumentParser(
            prog=argv[0] or self.APP_NAME,
            description=self.APP_DESCRIPTION,
            epilog=self.APP_EPILOG,
        )
        main_parser.add_argument(
            'command',
            nargs=1,
            type=str,
            choices=self.commands,
        )
        self.main_parser = main_parser

    @command
    def install(self):
        pass


    def main(self, argv):
        self.parse_argv(argv)

###

def entry_point(argv):
    cli = PyRunCLI()
    cli.main(sys.argv)

###

if __name__ == '__main__':
    cli = PyRunCLI()
