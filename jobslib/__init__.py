"""
Library for launching tasks in parallel environment.
"""

from .cmdlineparser import argument
from .config import Config, ConfigGroup, option
from .context import Context, cached_property
from .oneinstance import OneInstanceWatchdogError
from .tasks import BaseTask
from .version import VERSION

__all__ = [
    'argument', 'Config', 'ConfigGroup', 'option', 'Context',
    'cached_property', 'OneInstanceWatchdogError', 'BaseTask',
]

__version__ = VERSION
