"""
Module :module:`shelter.core.config` provides base class which
encapsulates configuration.
"""

import logging.config

from .context import Context
from .imports import import_object
from .logging import BASE_LOGGING
from .objectvalidator import option, OptionsContainer

__all__ = ['Config', 'ConfigGroup']


class ConfigGroup(OptionsContainer):
    """
    Container for configuration. During initialization are read values
    from all methods decorated by :class:`option` decorator . So if class
    is successfuly initialized, all options are validated a cached.
    """

    def initialize(self, *args, **unused_kwargs):
        """
        Initialize instance attributes. You can override this method in
        the subclasses.
        """
        self._settings, self._args_parser = args

    @property
    def as_kwargs(self):
        """
        Return all options as a :class:`dict`.
        """
        return {
            name: getattr(self, name)
            for name in option.get_option_names(self)
        }


class Config(OptionsContainer):
    """
    Class which encapsulates configuration. It joins configuration values
    from **settings** module and from command line. *settings* is a Python
    module defined by either ``JOBSLIB_SETTINGS_MODULE`` environment
    variable or ``-s/--settings`` command line argument. *args_parser* is
    an instance of the :class:`argparse.Namespace`.
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
        Configure Python logging according to configuration stored in the
        :attr:`logging` property.
        """
        logging.config.dictConfig(self.logging)

    @option
    def logging(self):
        """
        Python logging configuration as a :class:`dict` or
        :const:`BASE_LOGGING`.
        """
        return getattr(self._settings, 'LOGGING', BASE_LOGGING)

    @option
    def context_class(self):
        """
        Context class, either :class:`jobslib.Context` class or subclass.
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
        Configuration of the one instance lock. Contains attributes defined
        on :class:`OneInstanceConfig` class.
        """
        return OneInstanceConfig(
            getattr(self._settings, 'ONE_INSTANCE', {}), self._args_parser)

    @option
    def run_once(self):
        """
        Run task only once flag.
        """
        return self._args_parser.run_once

    @option
    def sleep_interval(self):
        """
        Sleep interval in seconds after task is done.
        """
        return self._args_parser.sleep_interval

    @option
    def liveness(self):
        """
        Configuration of the health status writer. Contains attributes
        defined on :class:`LivenessConfig` class.
        """
        return LivenessConfig(
            getattr(self._settings, 'LIVENESS', {}), self._args_parser)

    @option
    def consul(self):
        """
        Configuration of the connection arguments to HashiCorp Consul.
        Contains attributes defined on :class:`ConsulConfig` class.
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
        One instance lock implementation class. If ``--one-instance``
        argument is passed, value must be Python's module path. For
        development purposes you can use
        ``jobslib.oneinstance.dummy.DummyLock``.
        """
        if self._args_parser.one_instance:
            cls_name = self._settings['backend']
        else:
            cls_name = 'jobslib.oneinstance.dummy.DummyLock'
        return import_object(cls_name)

    @option
    def options(self):
        """
        Constructor's arguments of the one instance implementation class.
        It depends on :meth:`backend` attribute.
        """
        return self.backend.OptionsConfig(
            self._settings.get('options', {}), self._args_parser)


class LivenessConfig(ConfigGroup):
    """
    Configuration of the liveness writer.
    """

    @option
    def backend(self):
        """
        Liveness implementation class. If value is not defined, default
        value ``jobslib.liveness.dummy.DummyLiveness`` is used.
        """
        cls_name = self._settings.get(
            'backend', 'jobslib.liveness.dummy.DummyLiveness')
        return import_object(cls_name)

    @option
    def options(self):
        """
        Constructor's arguments of the liveness implementation class.
        """
        return self.backend.OptionsConfig(
            self._settings.get('options', {}), self._args_parser)


class ConsulConfig(ConfigGroup):
    """
    Configuration of the connection to HashiCorp Consul, see `Consul
    documentation <http://python-consul.readthedocs.io/en/latest/#consul>`_
    for details.
    """

    @option(attrtype=str)
    def scheme(self):
        """
        URI scheme, in current implementation always ``http``.
        """
        return 'http'

    @option(required=True, attrtype=str)
    def host(self):
        """
        IP address or hostname of the Consul server.
        """
        return self._settings.get('host', '')

    @option(attrtype=int)
    def port(self):
        """
        Port where the Consul server listening on.
        """
        return self._settings.get('port')
