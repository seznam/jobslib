"""
Command line parser helpers.
"""

import argparse
import sys

from colored import fg, attr

__all__ = ['argument']


def argument(*args, **kwargs):
    """
    Define how a single command-line argument should be parsed.
    *args* and *kwargs* have the same meaning as a
    :meth:`argparse.ArgumentParser.add_argument` method.
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
        self.exit(
            2, '\n{:s}{:s}: error: {}{:s}\n'.format(
                fg('red'), self.prog, message, attr('reset')))
