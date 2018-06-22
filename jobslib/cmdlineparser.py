"""
Command line parser helpers.
"""

import argparse
import sys

from gettext import gettext as _


def argument(*args, **kwargs):
    """
    Define how a single command-line argument should be parsed.
    *args* and *kwargs* have the same meaning as a
    :method:`argparse.ArgumentParser.add_argument` method.
    """
    return args, kwargs


class ArgumentParser(argparse.ArgumentParser):
    """
    Extends :class:`argparse.ArgumentParser` from Python's standard
    library. Overrides how the error message is printed.
    """

    def error(self, message):
        """
        Print on **stderr** error message from command line parser and
        exit process.
        """
        self.print_help(sys.stderr)
        self.exit(2, _('\n{:s}: error: {:s}\n').format(self.prog, message))
