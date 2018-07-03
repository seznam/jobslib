"""
Module :mod:`jobslib.oneinstance.dummy` provides :class:`DummyLock`
lock.
"""

from . import BaseLock

__all__ = ['DummyLock']


class DummyLock(BaseLock):
    """
    Dummy lock implementation. Do not provides real locking, all methods
    always return :const:`True`.
    """

    def acquire(self):
        return True

    def release(self):
        return True

    def refresh(self):
        return True
