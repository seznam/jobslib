"""
Module :mod:`jobslib.oneinstance.consul` provides :class:`ConsulLock`
lock. It is based on HashiCorp Consul, so lock is distributed among
datacenters.
"""

import collections.abc
import json
import logging
import signal
import os

from objectvalidator import option

from . import BaseLock, OneInstanceWatchdogError
from ..config import ConfigGroup
from ..time import get_current_time, to_local, to_utc

__all__ = ['ConsulLock']

logger = logging.getLogger(__name__)

ONE_DAY_SECONDS = 60 * 60 * 24


class ConsulLock(BaseLock):
    """
    Consul lock implementation, provides locking among datacenters.
    When the lock expires due to TTL, :exc:`OneInstanceWatchdogError`
    is raised. It is possible to extend the lock using :meth:`refresh`.
    Lock is not extended immediately, but request for extending is
    made and lock will be extended asynchronously when **SIGALRM** is
    received. So use conservative TTL and periodically extend the lock.

    .. warning::

        :class:`ConsulLock` uses :mod:`signal` and :data:`signal.SIGALRM`
        for TTL mechanism, so don't use :data:`~!signal.SIGALRM` in your
        task. And don't use multiple instances of the :class:`ConsulLock`
        at the same time, becase :data:`~!signal.SIGALRM` can't be shared
        among multiple instances.

    For using the :class:`ConsulLock` configure backend in :mod:`settings`:

    .. code-block:: python

        CONSUL = {
            'host': 'hostname',
            'port': 8500,
            'timeout': 1.0,
        }

        ONE_INSTANCE = {
            'backend': 'jobslib.oneinstance.consul.ConsulLock',
            'options': {
                'key': 'jobs/example/lock',
                'ttl': 60.0,
                'lock_delay': 15.0,
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

        @option(required=True, attrtype=int)
        def ttl(self):
            """
            Maximum lock lifespan in seconds, must be between 10 seconds
            and one day. If value is omitted, default is one day (maximum
            for Consul).
            """
            if 'JOBSLIB_ONE_INSTANCE_OPTIONS_TTL' in os.environ:
                ttl = int(os.environ['JOBSLIB_ONE_INSTANCE_OPTIONS_TTL'])
            else:
                ttl = self._settings.get('ttl', ONE_DAY_SECONDS)
            if ttl < 10 or ttl > ONE_DAY_SECONDS:
                raise ValueError(
                    'TTL must be between 10 and {} seconds'.format(
                        ONE_DAY_SECONDS))
            return ttl

        @option(required=True, attrtype=int)
        def lock_delay(self):
            """
            When sessions invalidation request is received, wait
            *lock_delay* seconds before session is truly invalidated.
            Value must be between 0 and 60 seconds, default is 1.
            """
            if 'JOBSLIB_ONE_INSTANCE_LOCK_DELAY' in os.environ:
                delay = int(os.environ.get('JOBSLIB_ONE_INSTANCE_LOCK_DELAY'))
            else:
                delay = self._settings.get('lock_delay', 1)
            if delay < 0 or delay > 60:
                raise ValueError('lock_delay must be between 0 and 60 seconds')
            return delay

    def __init__(self, context, options):
        super().__init__(context, options)
        self._session_id = None
        self._refresh_lock_flag = False

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
                self.options.key, json.dumps(record), acquire=session_id)
        except Exception:
            logger.exception("Can't acquire lock")
        else:
            if res is True:
                self._session_id = session_id
                self._refresh_lock_flag = False
                # Set SIGALRM refresh handler. If lock is not released or
                # extended before ttl is reached, task will be killed.
                signal.signal(signal.SIGALRM, self._alarm_handler)
                signal.alarm(self.options.ttl)
                return True
            logger.error("Can't acquire lock")
        self.context.consul.session.destroy(session_id)
        return False

    def release(self):
        try:
            res = self.context.consul.kv.put(
                self.options.key, None, release=self._session_id)
        except Exception:
            logger.exception("Can't release lock")
        else:
            if res is True:
                self._session_id = None
                self._refresh_lock_flag = False
                # Cancel SIGALRM
                signal.alarm(0)
                signal.signal(signal.SIGALRM, signal.SIG_DFL)
                return True
            logger.error("Can't release lock")
        return False

    def refresh(self):
        self._refresh_lock_flag = True
        return True

    def _alarm_handler(self, unused_signum, unused_frame):
        """
        **SIGALRM** signal handler, it is called at the end
        of Consuls' session TTL. Extend the lock if request
        for extending is presented, otherwise raise
        :exc:`OneInstanceWatchdogError`.
        """
        if self._refresh_lock_flag:
            try:
                res = self.context.consul.session.renew(self._session_id)
            except Exception:
                logger.exception("Can't extend lock")
            else:
                if res:
                    self._refresh_lock_flag = False
                    # Restart SIGALRM
                    signal.alarm(self.options.ttl)
                    return
                logger.error("Can't extend lock")
        raise OneInstanceWatchdogError

    def get_lock_owner_info(self):
        owner_info = None
        try:
            unused_index, res = self.context.consul.kv.get(self.options.key)
            if res is not None and res['Value'] is not None:
                owner_info = json.loads(res['Value'])
                if not isinstance(owner_info, collections.abc.Mapping):
                    raise ValueError('Lock owner info is not a JSON Object')
        except Exception:
            logger.exception("Can't get lock owner info")
        return owner_info
