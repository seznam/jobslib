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

import retrying

from consul import Consul
from objectvalidator import option

from . import BaseLock, OneInstanceWatchdogError
from ..config import ConfigGroup, RetryConfigMixin
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

        ONE_INSTANCE = {
            'backend': 'jobslib.oneinstance.consul.ConsulLock',
            'options': {
                'host': 'hostname',
                'port': 8500,
                'timeout': 1.0,
                'key': 'jobs/example/lock',
                'ttl': 60.0,
                'lock_delay': 15.0,
                'retry_max_attempts': 10,
                'retry_wait_multiplier': 50,
            },
        }

    Or use
    :envvar:`JOBSLIB_ONE_INSTANCE_CONSUL_HOST`,
    :envvar:`JOBSLIB_ONE_INSTANCE_CONSUL_PORT`,
    :envvar:`JOBSLIB_ONE_INSTANCE_CONSUL_TIMEOUT`,
    :envvar:`JOBSLIB_ONE_INSTANCE_CONSUL_KEY`,
    :envvar:`JOBSLIB_ONE_INSTANCE_CONSUL_TTL`,
    :envvar:`JOBSLIB_ONE_INSTANCE_CONSUL_LOCK_DELAY`,
    :envvar:`JOBSLIB_ONE_INSTANCE_CONSUL_RETRY_MAX_ATTEMPTS` and
    :envvar:`JOBSLIB_ONE_INSTANCE_CONSUL_RETRY_WAIT_MULTIPLIER`
    environment variables.
    """

    class OptionsConfig(RetryConfigMixin, ConfigGroup):
        """
        Consul lock options.
        """

        retry_env_prefix = 'JOBSLIB_ONE_INSTANCE_CONSUL_'

        @option(required=True, attrtype=str)
        def scheme(self):
            """
            URI scheme, in current implementation always ``http``.
            """
            return 'http'

        @option(required=True, attrtype=str)
        def host(self):
            """
            IP address or hostname of the Consul server.
            """
            host = os.environ.get('JOBSLIB_ONE_INSTANCE_CONSUL_HOST')
            if host:
                return host
            return self._settings.get('host', '127.0.0.1')

        @option(required=True, attrtype=int)
        def port(self):
            """
            Port where the Consul server listening on.
            """
            port = os.environ.get('JOBSLIB_ONE_INSTANCE_CONSUL_PORT')
            if port:
                return int(port)
            return self._settings.get('port', 8500)

        @option(required=True, attrtype=float)
        def timeout(self):
            """
            Timeout in seconds for connect/read/write operation.
            """
            timeout = os.environ.get('JOBSLIB_ONE_INSTANCE_CONSUL_TIMEOUT')
            if timeout:
                return float(timeout)
            timeout = self._settings.get('timeout', 5.0)
            if isinstance(timeout, int):
                timeout = float(timeout)
            return timeout

        @option(required=True, attrtype=str)
        def key(self):
            """
            Key under which the lock is stored.
            """
            key = os.environ.get('JOBSLIB_ONE_INSTANCE_CONSUL_KEY')
            if key:
                return key
            # env for backward compatibility
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
            if 'JOBSLIB_ONE_INSTANCE_CONSUL_TTL' in os.environ:
                ttl = int(os.environ['JOBSLIB_ONE_INSTANCE_CONSUL_TTL'])
            elif 'JOBSLIB_ONE_INSTANCE_OPTIONS_TTL' in os.environ:
                # env for backward compatibility
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
            if 'JOBSLIB_ONE_INSTANCE_CONSUL_LOCK_DELAY' in os.environ:
                delay = int(os.environ.get(
                    'JOBSLIB_ONE_INSTANCE_CONSUL_LOCK_DELAY'))
            elif 'JOBSLIB_ONE_INSTANCE_LOCK_DELAY' in os.environ:
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
        self._consul = Consul(
            scheme=self.options.scheme,
            host=self.options.host,
            port=self.options.port,
            timeout=self.options.timeout,
        )

    def acquire(self):
        @retrying.retry(
            stop_max_attempt_number=self.options.retry_max_attempts,
            wait_exponential_multiplier=self.options.retry_wait_multiplier)
        def _create_session():
            return self._consul.session.create(
                ttl=self.options.ttl, lock_delay=self.options.lock_delay)

        @retrying.retry(
            stop_max_attempt_number=self.options.retry_max_attempts,
            wait_exponential_multiplier=self.options.retry_wait_multiplier)
        def _acquire_lock(data, session_id):
            return self._consul.kv.put(
                self.options.key, data, acquire=session_id)

        @retrying.retry(
            stop_max_attempt_number=self.options.retry_max_attempts,
            wait_exponential_multiplier=self.options.retry_wait_multiplier)
        def _destroy_session(session_id):
            self._consul.session.destroy(session_id)

        timestamp = get_current_time()
        record = {
            'fqdn': self.context.fqdn,
            'timestamp': timestamp,
            'time_utc': to_utc(timestamp),
            'time_local': to_local(timestamp),
        }

        session_id = _create_session()
        try:
            res = _acquire_lock(json.dumps(record), session_id)
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
        _destroy_session(session_id)
        return False

    def release(self):
        @retrying.retry(
            stop_max_attempt_number=self.options.retry_max_attempts,
            wait_exponential_multiplier=self.options.retry_wait_multiplier)
        def _release_lock(session_id):
            return self._consul.kv.put(
                self.options.key, None, release=session_id)

        try:
            res = _release_lock(self._session_id)
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
        @retrying.retry(
            stop_max_delay=self.options.lock_delay,
            wait_exponential_multiplier=self.options.retry_wait_multiplier)
        def _renew_session(session_id):
            return self._consul.session.renew(session_id)

        if self._refresh_lock_flag:
            try:
                res = _renew_session(self._session_id)
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
        @retrying.retry(
            stop_max_attempt_number=self.options.retry_max_attempts,
            wait_exponential_multiplier=self.options.retry_wait_multiplier)
        def _get_lock_owner_info():
            return self._consul.kv.get(self.options.key)[1]

        owner_info = None
        try:
            res = _get_lock_owner_info()
            if res is not None and res['Value'] is not None:
                owner_info = json.loads(res['Value'])
                if not isinstance(owner_info, collections.abc.Mapping):
                    raise ValueError('Lock owner info is not a JSON Object')
        except Exception:
            logger.exception("Can't get lock owner info")
        return owner_info
