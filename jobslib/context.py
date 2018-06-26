"""
Module :module:`jobslib.context` provides base class which encapsulates
necessary resources (configuration, database connection, …) for tasks.
"""

from cached_property import cached_property
from consul import Consul

__all__ = ['Context']


class Context(object):
    """
    Class which encapsulates resources (configuration, database
    connection, …) for tasks.
    """

    def __init__(self, config):
        self._config = config
        self.initialize()

    @classmethod
    def from_config(cls, config):
        """
        According to application's configuration *config* create and
        return new instance of the **Context**.
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
        Application's configuration.
        """
        return self._config

    @cached_property
    def consul(self):
        """
        Connection arguments to HashiCorp Consul.
        """
        kwargs = {
            k: v for k, v in self._config.consul.as_kwargs.items()
            if v is not None}
        return Consul(**kwargs)
