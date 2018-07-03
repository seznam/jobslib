"""
Module :mod:`jobslib.liveness.dummy` provides :class:`DummyLiveness`
writer.
"""

from . import BaseLiveness

__all__ = ['DummyLiveness']


class DummyLiveness(BaseLiveness):
    """
    Dummy liveness implementation. Do not provides real functionality.
    """

    def write(self):
        pass
