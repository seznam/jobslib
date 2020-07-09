"""
Module :mod:`jobslib.context` provides base class which encapsulates
necessary resources (configuration, database connection, …) for tasks.
"""

import socket

from cached_property import cached_property

__all__ = ['Context']


class Context(object):
    """
    Class which encapsulates resources (configuration, database connection,
    …). Instance of this class is created during task initialization. So in
    your task you have access to all necessary resources. Inherit this class
    and enrich it of necessary properties. According to your requirements
    cache values using :func:`cached_property` decorator.

    Example of the custom :class:`Context` class:

    .. code-block:: python

        from xmlrpc.client import ServerProxy

        from jobslib import Context, cached_property

        class MyAppContext(Context):

            @cached_property
            def auth_service(self):
                return ServerProxy(uri=self.config.auth_service.uri)

    And write into :mod:`settings` module:

    .. code-block:: python

        CONTEXT_CLASS = 'myapp.context.MyAppContext'
    """

    def __init__(self, config):
        self._config = config
        self.initialize()

    @classmethod
    def from_config(cls, config):
        """
        According to application's configuration *config* create and
        return new instance of the :class:`Context`.
        """
        return cls(config)

    def initialize(self):
        """
        Initialize instance attributes. You can override this method in
        the subclasses.
        """
        pass

    @cached_property
    def config(self):
        """
        Application's configuration, instance of the :class:`~jobslib.Config`.
        """
        return self._config

    @cached_property
    def fqdn(self):
        """
        Fully qualified domain name of the local machine as :class:`!str`.
        """
        return socket.getfqdn()

    @cached_property
    def one_instance_lock(self):
        """
        One instance lock, instance of the
        :class:`jobslib.oneinstance.BaseLock` descendant.
        """
        return self._config.one_instance.backend(
            self, self._config.one_instance.options)

    @cached_property
    def liveness(self):
        """
        Health state writer, instance of the
        :class:`jobslib.liveness.BaseLiveness` descendant.
        """
        return self._config.liveness.backend(
            self, self._config.liveness.options)

    @cached_property
    def metrics(self):
        """
        Metrics writer, instance of the
        :class:`jobslib.liveness.BaseMetrics` descendant.
        """
        return self._config.metrics.backend(
            self, self._config.metrics.options)
