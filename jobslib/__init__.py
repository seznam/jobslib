"""
Library for launching tasks in parallel environment. Task is launched from
command line using ``runjob`` command:

.. code-block:: bash

    runjob [-s SETTINGS] [--disable-one-instance] [--run-once]
           [--sleep-interval SLEEP_INTERVAL]
           task_cls

    runjob -s myapp.settings myapp.task.HelloWorld --run-once

    export JOBSLIB_SETTINGS_MODULE="myapp.settings"
    runjob myapp.task.HelloWorld --run-once

Task is normally run in infinite loop, delay in seconds between individual
launches is controlled by ``--sleep-interval`` argument. If you don't want
to launch task forever, use ``--run-once`` argument. Library provides
locking mechanism for launching tasks on several machines and only one
instance at one time may be launched. If you don't want this locking, use
``--disable-one-instance`` argument. All these options can be set in
**settings** module. Optional argument ``--settings`` defines Python's
module where configuration is stored. Or you can pass settings module
using ``JOBSLIB_SETTINGS_MODULE``.

During task initialization instances of the :class:`Config` and
:class:`Context` classes are created. You can define your own classes in the
**settings** module. :class:`Config` is container which holds configuration.
:class:`Context` is container which holds resources which are necessary for
your task, for example database connection. Finally, when both classes are
successfuly initialized, instance of the task (subclass of the
:class:`BaseTask` passed as ``task_cls`` argument) is created and launched.

If you want to write your own task, inherit :class:`BaseTask` class and
override :meth:`BaseTask.task` method. According to your requirements
inherit and override :class:`Config` and/or :class:`Context` and set
**settings** module.
"""

import os.path
import re

from .cmdlineparser import argument
from .config import Config, ConfigGroup, option
from .context import Context, cached_property
from .tasks import BaseTask

__all__ = [
    'BaseTask', 'argument', 'Config', 'ConfigGroup', 'option',
    'Context', 'cached_property'
]


def _get_version():
    filename = os.path.join(os.path.dirname(__file__), 'CHANGELOG.md')
    with open(filename, 'rt') as fd:
        pat = r"""
            (?P<version>\d+\.\d+)         # minimum 'N.N'
            (?P<extraversion>(?:\.\d+)*)  # any number of extra '.N' segments
            (?:
                (?P<prerel>[abc]|rc)      # 'a' = alpha, 'b' = beta
                                          # 'c' or 'rc' = release candidate
                (?P<prerelversion>\d+(?:\.\d+)*)
            )?
            (?P<postdev>(\.post(?P<post>\d+))?(\.dev(?P<dev>\d+))?)?
        """
        for line in fd:
            match = re.search(pat, line, re.VERBOSE)
            if match:
                return match.group()
    raise ValueError("Can't get version")


__version__ = _get_version()
