"""
Module :mod:`jobslib.oneinstance.consul` provides :class:`ConsulLock`
lock. It is based on HashiCorp Consul, so lock is distributed among
datacenters.
"""

import logging
import signal
import os

import ujson

from objectvalidator import option

from . import BaseLock, OneInstanceWatchdogError
from ..config import ConfigGroup
from ..time import get_current_time, to_local, to_utc

__all__ = ['ConsulLock']

logger = logging.getLogger(__name__)


class ConsulLock(BaseLock):
    """
    Consul lock implementation. Provides locking among datacenters.
    When the lock expires due to TTL, :exc:`OneInstanceWatchdogError` is
    raised.

    .. warning::

        :class:`ConsulLock` uses :mod:`signal` and :data:`signal.SIGALRM`
        for TTL mechanism, so don't use :data:`signal.SIGALRM` in your
        task.

    For using the :class:`ConsulLock` write into **settings**:

    .. code-block:: python

        ONE_INSTANCE = {
            'backend': 'jobslib.oneinstance.consul.ConsulLock',
            'options': {
                'key': 'jobs/example/lock',
                'ttl': 60,
            },
        }
    """

    class OptionsConfig(ConfigGroup):
        """
        Consul lock options.
        """

        @option(required=True, attrtype=str)
        def key(self):
            """
            Key under which the lock is stored.
            """
            key = os.environ.get('JOBSLIB_ONE_INSTANCE_OPTIONS_KEY')
            if key:
                return key
            return self._settings['key']

        @option(attrtype=int)
        def ttl(self):
            """
            Maximum lock lifespan in seconds.
            """
            one_day_seconds = 60 * 60 * 24

            ttl = os.environ.get('JOBSLIB_ONE_INSTANCE_OPTIONS_TTL')
            if ttl:
                ttl = int(ttl)
            else:
                ttl = self._settings.get('ttl', one_day_seconds)
            if ttl < 10 or ttl > one_day_seconds:
                raise ValueError(
                    'TTL must be between 10 and {} seconds'.format(
                        one_day_seconds))
            return ttl

        @option(attrtype=int)
        def lock_delay(self):
            """
            When sessions invalidation request is received, wait *lock_delay*
            seconds before session is truly invalidated. Valid value must be
            between 0 and 60 seconds, default is 1.
            """
            lock_delay = os.environ.get('JOBSLIB_ONE_INSTANCE_LOCK_DELAY')
            if lock_delay:
                lock_delay = int(lock_delay)
            else:
                lock_delay = self._settings.get('lock_delay', 1)
            if lock_delay < 0 or lock_delay > 60:
                raise ValueError('lock_delay must be between 0 and 60 seconds')
            return lock_delay

    def __init__(self, context, options):
        super().__init__(context, options)
        self.session_id = None

    @staticmethod
    def alarm_handler(unused_signum, unused_frame):
        """
        Raise :exc:`OneInstanceWatchdogError` when TTL of the lock is
        reached.
        """
        raise OneInstanceWatchdogError

    def acquire(self):
        timestamp = get_current_time()
        record = {
            'fqdn': self.context.fqdn,
            'timestamp': timestamp,
            'time_utc': to_utc(timestamp),
            'time_local': to_local(timestamp),
        }

        session_id = self.context.consul.session.create(
            ttl=self.options.ttl, lock_delay=self.options.lock_delay)
        try:
            res = self.context.consul.kv.put(
                self.options.key, ujson.dumps(record), acquire=session_id)
        except Exception:
            logger.exception("Can't acquire lock")
            self.context.consul.session.destroy(session_id)
            return False
        else:
            if res is True:
                self.session_id = session_id
                # Set SIGALRM handler. If lock is not released before ttl,
                # process will be killed.
                signal.signal(signal.SIGALRM, self.alarm_handler)
                signal.alarm(self.options.ttl)
                return True

            self.context.consul.session.destroy(session_id)
            return False

    def release(self):
        try:
            res = self.context.consul.kv.put(
                self.options.key, None, release=self.session_id)
        except Exception:
            logger.exception("Can't release lock")
            return False
        else:
            self.session_id = None
            if res is True:
                # Cancel SIGALRM
                signal.alarm(0)
                signal.signal(signal.SIGALRM, signal.SIG_DFL)
                return True
            return False

    def refresh(self):
        try:
            res = self.context.consul.session.renew(self.session_id)
        except Exception:
            logger.exception("Can't refresh lock")
            return False
        else:
            if res:
                # Restart SIGALRM
                signal.alarm(self.options.ttl)
                return True
            return True

    def get_lock_owner_info(self):
        unused_index, res = self.context.consul.kv.get(self.options.key)
        if (res is not None) and (res['Value'] is not None):
            value = ujson.loads(res['Value'])
            return "{}, locked at {} UTC".format(
                value.get('fqdn'), value.get('time_utc'))
        return None
