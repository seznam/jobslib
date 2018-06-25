"""
Module :module:`shelter.core.config` provides base class which
encapsulates configuration.
"""

import logging.config

from .cmdlineparser import argument
from .context import Context
from .imports import import_object
from .logging import BASE_LOGGING
from .objectvalidator import option, OptionsContainer

__all__ = ['Config', 'argument']


class Config(OptionsContainer):
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
        super().__init__()

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
        :attr:`logging`.
        """
        logging.config.dictConfig(self.logging)

    @option
    def logging(self):
        """
        Python logging configuration as a :class:`dict` or
        :data:`BASE_LOGGING`.
        """
        return getattr(self._settings, 'LOGGING', BASE_LOGGING)

    @option
    def context_class(self):
        """
        Context class, either :class:`jobslib.context.Context` class or
        subclass.
        """
        context_cls_name = getattr(self._settings, 'CONTEXT_CLASS', '')
        if context_cls_name:
            context_class = import_object(context_cls_name)
        else:
            context_class = Context
        return context_class
