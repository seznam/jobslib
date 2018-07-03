"""
Library for launching tasks in parallel environment. Inherit
:class:`BaseTask` class, override :meth:`BaseTask.task` method
and run your task from console:

.. code-block:: bash

    runjob [-s SETTINGS] path.to.TaskClass
"""

from .cmdlineparser import argument
from .config import Config, ConfigGroup, option
from .context import Context
from .tasks import BaseTask

__all__ = [
    'BaseTask', 'argument', 'Config', 'Context', 'ConfigGroup', 'option'
]
