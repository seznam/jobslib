"""
Module :mod:`jobslib.liveness.consul` provides :class:`ConsulLiveness`
writer.
"""

import json
import logging
import os

import retrying

from consul import Consul
from objectvalidator import option

from . import BaseLiveness
from ..config import ConfigGroup, RetryConfigMixin

__all__ = ['ConsulLiveness']

logger = logging.getLogger(__name__)


class ConsulLiveness(BaseLiveness):
    """
    Consul liveness implementation. Provides exporting informations about
    health state into Consul's key/value storage.

    For use of :class:`ConsulLiveness` write into :mod:`settings`:

    .. code-block:: python

        LIVENESS = {
            'backend': 'jobslib.liveness.consul.ConsulLiveness',
            'options': {
                'host': 'hostname',
                'port': 8500,
                'timeout': 1.0,
                'key': 'jobs/example/liveness',
                'retry_max_attempts': 10,
                'retry_wait_multiplier': 50,
            },
        }

    Or use
    :envvar:`JOBSLIB_LIVENESS_CONSUL_HOST`,
    :envvar:`JOBSLIB_LIVENESS_CONSUL_PORT`,
    :envvar:`JOBSLIB_LIVENESS_CONSUL_TIMEOUT`,
    :envvar:`JOBSLIB_LIVENESS_CONSUL_KEY`,
    :envvar:`JOBSLIB_LIVENESS_CONSUL_RETRY_MAX_ATTEMPTS` and
    :envvar:`JOBSLIB_LIVENESS_CONSUL_RETRY_WAIT_MULTIPLIER`
    environment variables.
    """

    class OptionsConfig(RetryConfigMixin, ConfigGroup):
        """
        Consul liveness options.
        """

        retry_env_prefix = 'JOBSLIB_LIVENESS_CONSUL_'

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
            host = os.environ.get('JOBSLIB_LIVENESS_CONSUL_HOST')
            if host:
                return host
            return self._settings.get('host', '127.0.0.1')

        @option(required=True, attrtype=int)
        def port(self):
            """
            Port where the Consul server listening on.
            """
            port = os.environ.get('JOBSLIB_LIVENESS_CONSUL_PORT')
            if port:
                return int(port)
            return self._settings.get('port', 8500)

        @option(required=True, attrtype=float)
        def timeout(self):
            """
            Timeout in seconds for connect/read/write operation.
            """
            timeout = os.environ.get('JOBSLIB_LIVENESS_CONSUL_TIMEOUT')
            if timeout:
                return float(timeout)
            timeout = self._settings.get('timeout', 5.0)
            if isinstance(timeout, int):
                timeout = float(timeout)
            return timeout

        @option(required=True, attrtype=str)
        def key(self):
            """
            Key under which the health state is stored.
            """
            key = os.environ.get('JOBSLIB_LIVENESS_CONSUL_KEY')
            if key:
                return key
            return self._settings['key']

    def __init__(self, context, options):
        super().__init__(context, options)
        self._consul = Consul(
            scheme=self.options.scheme,
            host=self.options.host,
            port=self.options.port,
            timeout=self.options.timeout,
        )

    def write(self):
        @retrying.retry(
            stop_max_attempt_number=self.options.retry_max_attempts,
            wait_exponential_multiplier=self.options.retry_wait_multiplier)
        def _write(data):
            return self._consul.kv.put(self.options.key, data)

        try:
            state = self.get_state()
            data = json.dumps(state)
            if not _write(data):
                logger.error("Can't write liveness state")
        except Exception:
            logger.exception("Can't write liveness state")

    def read(self):
        @retrying.retry(
            stop_max_attempt_number=self.options.retry_max_attempts,
            wait_exponential_multiplier=self.options.retry_wait_multiplier)
        def _read():
            return self._consul.kv.get(self.options.key)[1]

        try:
            data = _read()
            if data is None:
                raise KeyError(self.options.key)
            record = json.loads(data['Value'])
        except Exception:
            logger.exception("Can't read liveness state")
            raise
        return record
