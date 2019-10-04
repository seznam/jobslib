"""
Module :mod:`jobslib.oneinstance.dummy` provides :class:`DummyLock`
lock.
"""

from . import BaseLock

__all__ = ['DummyLock']


class DummyLock(BaseLock):
    """
    Dummy lock implementation. Doesn't provide real locking, all methods
    always return :data:`True`. It is useful for development or if it is
    not necessary run only one instance at the same time. For using the
    :class:`DummyLock` configure backend in **settings**:

    .. code-block:: python

        ONE_INSTANCE = {
            'backend': 'jobslib.oneinstance.dummy.DummyLock',
        }
    """

    def acquire(self):
        return True

    def release(self):
        return True

    def refresh(self):
        return True
