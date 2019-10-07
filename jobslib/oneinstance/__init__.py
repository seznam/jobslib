"""
Module :mod:`oneinstance` provides a lock which allowes only one running
instance at the same time. The Lock is used when ``--one-instance`` command
line argument is passed. When acquiring the lock is not possible, task is not
run and process is slept for ``--sleep-interval`` seconds. Then ``runjob``
will try to acquire lock again. If implementation of the lock supports TTL
and you need extend the lock, it is possible call :meth:`BaseLock.refresh`
inside your :meth:`jobslib.BaseTask.task`. Otherwise task is aborted.

:class:`BaseLock` is ancestor, it is an abstract class which defines API,
not locking functionality. Override the class if you want write own
implementation of the lock.
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
    Provides lock's API. Inherit this class and override abstract methods
    :meth:`acquire`, :meth:`release` and :meth:`refresh`. Configuration
    options are defined in :class:`OptionsConfig` class, which is
    :class:`~jobslib.ConfigGroup` descendant.
    """

    class OptionsConfig(ConfigGroup):
        """
        Validation of the lock's configuration, see
        :class:`~jobslib.ConfigGroup`.
        """
        pass

    def __init__(self, context, options):
        self.context = context
        self.options = options

    @abc.abstractmethod
    def acquire(self):
        """
        Acquire a lock. Return :data:`True` if lock has been successfuly
        acquired, otherwise return :data:`False`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def release(self):
        """
        Release existing lock. Return :data:`True` if lock has been
        successfuly released, otherwise return :data:`False`.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def refresh(self):
        """
        Refresh existing lock. Return :data:`True` if lock has been
        successfuly refreshed, otherwise return :data:`False`.
        """
        raise NotImplementedError

    def get_lock_owner_info(self):
        """
        Return lock's owner information. It depends on implementation,
        return :class:`dict` or :data:`None` if information is not
        available.
        """
        return None
