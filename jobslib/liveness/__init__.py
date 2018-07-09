"""
Module :mod:`liveness` provides functionality for exporting informations
about health state of the task. When task is successfuly finished,
some state is written. :class:`BaseLiveness` is ancestor, it is abstract
class which defines API, not functionality. Override this class if you
want to write own implementation of the liveness.
"""

import abc

from ..config import ConfigGroup
from ..time import get_current_time, to_utc

__all__ = ['BaseLiveness']


class BaseLiveness(abc.ABC):
    """
    Provides liveness API. Inherit this class and override abstract method
    :meth:`write`. Configuration options are defined in
    :class:`OptionsConfig` class, which is :class:`~jobslib.ConfigGroup`
    descendant.
    """

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
    def write(self):
        """
        Write informations about health state of the task.
        """
        raise NotImplementedError

    def get_state(self):
        """
        Return health state as a :class:`str`.
        """
        return to_utc(get_current_time(), format_string='%Y/%m/%d/%H/%M/%S')
