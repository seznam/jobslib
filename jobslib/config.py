"""
Module :module:`shelter.core.config` provides base class which
encapsulates configuration.
"""

import logging.config

from jobslib.cmdlineparser import argument
from jobslib.context import Context
from jobslib.imports import import_object
from jobslib.logging import BASE_LOGGING

__all__ = ['Config', 'argument']


class Config(object):
    """
    Class which encapsulates configuration. It joins options from settings
    module and from command line. *settings* is a Python module defined by
    either **JOBSLIB_SETTINGS_MODULE** environment variable or
    **-s/--settings** command line argument. *args_parser* is an instance
    of the :class:`argparse.Namespace`.
    """

    arguments = ()
    """
    Command line arguments of the Config class.
    """

    def __init__(self, settings, args_parser):
        self._settings = settings
        self._args_parser = args_parser
        self.initialize()

    def __repr__(self):
        return "<{}.{}: {:#x}>".format(
            self.__class__.__module__, self.__class__.__name__, id(self)
        )

    def initialize(self):
        """
        Initialize instance attributes. You can override this method in
        the subclasses.
        """
        pass

    def configure_logging(self):
        """
        Configure Python logging according to configuration in
        :meth:`config`.
        """
        logging.config.dictConfig(self.logging)

    @property
    def logging(self):
        """
        Python logging configuration as a :class:`dict` or
        :const:`BASE_LOGGING`.
        """
        return getattr(self.settings, 'LOGGING', BASE_LOGGING)

    @property
    def context_class(self):
        """
        Context class, either :class:`jobslib.context.Context` class or
        subclass.
        """
        if 'context_class' not in self._cached_values:
            context_cls_name = getattr(self.settings, 'CONTEXT_CLASS', '')
            if context_cls_name:
                context_class = import_object(context_cls_name)
            else:
                context_class = Context
            self._cached_values['context_class'] = context_class
        return self._cached_values['context_class']
