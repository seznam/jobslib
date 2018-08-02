"""
Module :mod:`liveness` provides functionality for exporting informations
about health state of the task. When task is successfuly finished,
some state is written. :class:`BaseLiveness` is ancestor, it is abstract
class which defines API, not functionality. Override this class if you
want to write own implementation of the liveness.
"""

import abc
import sys

from ..cmdlineparser import argument
from ..config import ConfigGroup
from ..tasks import _Task
from ..time import get_current_time, to_utc, to_local

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

    @abc.abstractmethod
    def read(self):
        """
        Read informations about health state of the task.
        """
        raise NotImplementedError

    def check(self, max_age):
        """
        Check liveness and return :data:`True` when liveness timestamp is
        younger than *max_age*, :data:`False` when liveness timestamp is
        older than *max_age*.
        """
        record = self.read()
        timestamp = get_current_time()
        if (timestamp - record['timestamp']) > max_age:
            return False
        return True

    def get_state(self):
        """
        Return health state as a :class:`str`.
        """
        timestamp = get_current_time()
        return {
            'fqdn': self.context.fqdn,
            'timestamp': timestamp,
            'time_utc': to_utc(timestamp),
            'time_local': to_local(timestamp),
        }


class CheckLiveness(_Task):
    """
    Internal task which checkes age of the liveness stamp. Returns exit
    code :const:`0` if check passes, :const:`0` if check fails.
    """

    name = 'check-liveness'
    description = 'check if liveness is valid'
    arguments = (
        argument(
            '--max-age', action='store', dest='max_age',
            type=int, required=True,
            help='maximun age of the liveness stamp in seconds'),
    )

    def initialize(self):
        self.max_age = self.context.config._args_parser.max_age

    def task(self):
        if self.max_age <= 0:
            raise ValueError("Invalid max_age: {}".format(self.max_age))
        if self.context.liveness.check(self.max_age):
            sys.stdout.write('PASS\n')
            sys.stdout.flush()
            sys.exit(0)
        else:
            sys.stdout.write('FAIL\n')
            sys.stdout.flush()
            sys.exit(1)
