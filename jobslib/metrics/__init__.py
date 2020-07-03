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
    def push(self, metrics):
        """
        Push metrics. *metrics* are :class:`!dict`, where key is metric
        name and value is :class:`!dict` structure containing value and
        optionally tags.

        .. code-block:: python

            metrics = {
                "flow_velocity": {
                    "value": 30.0,
                    "tags": {
                        "tag_name1": "tag_value1",
                        "tag_name2": "tag_value2",
                    },
                },
                "processed_requests": {
                    "value": 5,
                    "tags": {
                        "tag_name3": "tag_value3",
                    },
                },
            }
        """
        raise NotImplementedError
