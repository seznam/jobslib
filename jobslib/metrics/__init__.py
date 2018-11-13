"""
Provides metrics API. Inherit this class and override abstract method
:meth:`push_monitoring_metrics`. Configuration options are defined in
:class:`OptionsConfig` class, which is :class:`~jobslib.ConfigGroup`
descendant.
"""

import abc

from jobslib import ConfigGroup

__all__ = ['BaseMetrics']


class BaseMetrics(abc.ABC):
    class OptionsConfig(ConfigGroup):
        """
        Validation of the liveness configuration, see
        :class:`~jobslib.ConfigGroup`.
        """
        pass

    def __init__(self, context, options):
        self.context = context
        self.options = options

    @abc.abstractmethod
    def push_monitoring_metrics(self, metrics, timestamp=None):
        """ Push metrics
        :param metrics: Metrivs
        :param timestamp: Timestamp

        :type metrics: Dict[str, Union[int, float]]
        :type timestamp: Union[int, float, None]
        """
        raise NotImplementedError
