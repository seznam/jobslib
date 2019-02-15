"""
Module :mod:`jobslib.liveness.consul` provides :class:`ConsulLiveness`
writer.
"""

import logging
import os

import ujson

from objectvalidator import option

from . import BaseLiveness
from ..config import ConfigGroup

__all__ = ['ConsulLiveness']

logger = logging.getLogger(__name__)


class ConsulLiveness(BaseLiveness):
    """
    Consul liveness implementation. Provides exporting informations about
    health state into Consul's key/value storage.

    For use of :class:`ConsulLiveness` write into **settings**:

    .. code-block:: python

        LIVENESS = {
            'backend': 'jobslib.liveness.consul.ConsulLiveness',
            'options': {
                'key': 'jobs/example/liveness',
            },
        }
    """

    class OptionsConfig(ConfigGroup):
        """
        Consul liveness options.
        """

        @option(required=True, attrtype=str)
        def key(self):
            """
            Key under which the health state is stored.
            """
            key = os.environ.get('JOBSLIB_LIVENESS_OPTIONS_KEY')
            if key:
                return key
            return self._settings['key']

    def write(self):
        try:
            state = self.get_state()
            data = ujson.dumps(state)
            if not self.context.consul.kv.put(self.options.key, data):
                logger.error("Can't write liveness state")
        except Exception:
            logger.exception("Can't write liveness state")

    def read(self):
        try:
            unused_index, data = self.context.consul.kv.get(self.options.key)
            if data is None:
                raise KeyError(self.options.key)
            record = ujson.loads(data['Value'])
        except Exception:
            logger.exception("Can't read liveness state")
            raise
        return record
