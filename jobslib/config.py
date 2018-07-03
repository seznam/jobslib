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

__all__ = ['Config', 'ConfigGroup']


class ConfigGroup(OptionsContainer):

    def initialize(self, *args, **unused_kwargs):
        self._settings, self._args_parser = args

    @property
    def as_kwargs(self):
        return {
            name: getattr(self, name)
            for name in option.get_option_names(self)
        }


class Config(OptionsContainer):
    """
    Class which encapsulates configuration. It joins options from settings
    module and from command line. *settings* is a Python module defined by
    either **JOBSLIB_SETTINGS_MODULE** environment variable or
    **-s/--settings** command line argument. *args_parser* is an instance
    of the :class:`argparse.Namespace`.
    """

    _base_arguments = (
        argument(
            '--one-instance', action='store_true',
            dest='one_instance', default=False,
            help='only one running instance at the same time is allowed'),
    )

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

    def initialize(self, *args, **kwargs):
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

    @option
    def one_instance(self):
        """
        One instance lock.
        """
        return OneInstanceConfig(
            getattr(self._settings, 'ONE_INSTANCE', {}), self._args_parser)

    @option
    def consul(self):
        """
        Connection arguments to HashiCorp Consul, see `Consul documentation
        <http://python-consul.readthedocs.io/en/latest/#consul>`_.
        .
        """
        return ConsulConfig(
            getattr(self._settings, 'CONSUL', {}), self._args_parser)


class OneInstanceConfig(ConfigGroup):
    """
    Configuration of the one instance lock.
    """

    @option
    def backend(self):
        """
        One instance implementation class.
        """
        if self._args_parser.one_instance:
            cls_name = self._settings['backend']
        else:
            cls_name = 'jobslib.oneinstance.dummy.DummyLock'
        return import_object(cls_name)

    @option
    def options(self):
        """
        Constructor arguments of the one instance implementation class.
        Config group class is adopted from :meth:`backend`.
        """
        return self.backend.OptionsConfig(
            self._settings.get('options', {}), self._args_parser)


class ConsulConfig(ConfigGroup):
    """
    Connection arguments to HashiCorp Consul, see `Consul documentation
    <http://python-consul.readthedocs.io/en/latest/#consul>`_.
    """

    @option(attrtype=str)
    def scheme(self):
        """
        URI scheme.
        """
        return 'http'

    @option(required=True, attrtype=str)
    def host(self):
        """
        IP address or hostname of the Consul server.
        """
        return self._settings['host']

    @option(attrtype=int)
    def port(self):
        """
        Port of the Consul server.
        """
        return self._settings.get('port')
