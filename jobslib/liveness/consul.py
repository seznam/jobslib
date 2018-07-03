"""
Module :mod:`jobslib.liveness.consul` provides :class:`ConsulLiveness`
writer.
"""

import logging

from . import BaseLiveness
from ..config import ConfigGroup
from ..objectvalidator import option

__all__ = ['ConsulLiveness']

logger = logging.getLogger(__name__)


class ConsulLiveness(BaseLiveness):
    """
    Consul liveness implementation. Provides exporting health state into
    Consul key/value storage.
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
            return self._settings['key']

    def write(self):
        try:
            state = self.get_state()
            if not self.context.consul.kv.put(self.options.key, state):
                logger.exception("Can't write liveness")
        except Exception:
            logger.exception("Can't write liveness")
