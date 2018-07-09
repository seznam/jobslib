"""
Module :mod:`jobslib.liveness.consul` provides :class:`ConsulLiveness`
writer.
"""

import logging
import os

from . import BaseLiveness
from ..config import ConfigGroup
from ..objectvalidator import option

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
            key = os.environ.get('DOP_JOBSLIB_LIVENESS_OPTIONS_KEY')
            if key is not None:
                return key
            return self._settings['key']

    def write(self):
        try:
            state = self.get_state()
            if not self.context.consul.kv.put(self.options.key, state):
                logger.exception("Can't write liveness")
        except Exception:
            logger.exception("Can't write liveness")
