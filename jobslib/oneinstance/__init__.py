"""
Module :mod:`oneinstance` provides lock which allowes only one running
instance at the same time.
"""

import abc

from ..config import ConfigGroup

__all__ = ['BaseLock', 'OneInstanceWatchdogError']


class OneInstanceWatchdogError(BaseException):
    """
    Indicates that TTL of the lock has been reached.
    """
    pass


class BaseLock(abc.ABC):
    """
    Provides lock API. Inherit this class and override abstract methods
    :meth:`acquire`, :meth:`release` and :meth:`refresh`.
    """

    class OptionsConfig(ConfigGroup):
        """
        Validation of the lock *options*.
        """
        pass

    def __init__(self, context, options):
        self.context = context
        self.options = options

    @abc.abstractmethod
    def acquire(self):
        """
        Acquire a lock. Return :const:`True` if lock has been successfuly
        acquired, otherwise return :const:`False`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def release(self):
        """
        Release existing lock. Return :const:`True` if lock has been
        successfuly released, otherwise return :const:`False`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def refresh(self):
        """
        Refresh existing lock. Return :const:`True` if lock has been
        successfuly refreshed, otherwise return :const:`False`.
        """
        raise NotImplementedError

    def get_lock_owner_info(self):
        """
        Return information about owner of the lock. It depends on
        implementation, return :data:`None` if information is not
        available.
        """
        return None
