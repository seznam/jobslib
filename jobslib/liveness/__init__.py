"""
Module :mod:`liveness` provides functionality for exportig healt status
of the task.
"""

import abc

from ..config import ConfigGroup
from ..time import get_current_time, to_utc

__all__ = ['BaseLiveness']


class BaseLiveness(abc.ABC):
    """
    Provides liveness API.
    """

    class OptionsConfig(ConfigGroup):
        """
        Validation of the liveness *options*.
        """
        pass

    def __init__(self, context, options):
        self.context = context
        self.options = options

    @abc.abstractmethod
    def write(self):
        """
        Write health state of the task.
        """
        raise NotImplementedError

    def get_state(self):
        """
        Return state as a :class:`string`.
        """
        return to_utc(get_current_time(), format_string='%Y/%m/%d/%H/%M/%S')
