"""
Module :mod:`jobslib.liveness.dummy` provides :class:`DummyLiveness`
writer.
"""

from . import BaseLiveness

__all__ = ['DummyLiveness']


class DummyLiveness(BaseLiveness):
    """
    Dummy liveness implementation. Doesn't provide real functionality.
    It is useful for development or if it is not necessary liveness. For
    use of :class:`DummyLiveness` write into **settings**:

    .. code-block:: python

        LIVENESS = {
            'backend': 'jobslib.liveness.dummy.DummyLiveness',
        }
    """

    def write(self):
        pass

    def read(self):
        return self.get_state()
