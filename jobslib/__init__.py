"""
Library for launching tasks in parallel environment. Task is launched from
command line using ``runjob`` command:

.. code-block:: bash

    runjob [-s SETTINGS] [--one-instance] [--run-once]
           [--sleep-interval SLEEP_INTERVAL]
           task_cls

    runjob -s myapp.settings myapp.task.HelloWorld --run-once

    export JOBSLIB_SETTINGS_MODULE="myapp.settings"
    runjob -s myapp.task.HelloWorld --run-once

Task is normally run in infinite loop, delay in seconds between individual
launch is controlled by ``--sleep-interval`` argument. If you don't want
to launch task forever, use ``--run-once`` argument. If you launch task on
several machines and task can be launched only one instance at one time,
library provides locking mechanism. In this case use ``--one-instance``
argument. Optional argument ``--settings`` defines Python's module where
configuration is stored. Or you can pass settings module using
``JOBSLIB_SETTINGS_MODULE``.

During task initialization are created instances of the :class:`Config` and
:class:`Context` classes. You can define your own classes in the **settings**
module. :class:`Config` is a container which holds configuration.
:class:`Context` is a container which holds resources which are necessary
for your task, for example database connection. Finally, when both classes
are successfuly initialized, instance of the task (subclass of the
:class:`BaseTask` passed as a ``task_cls`` argument) is created and launched.

If you want to write your own task, make **settings** module, inherit
:class:`BaseTask` class and override :meth:`BaseTask.task` method. According
to your requirements inherit and override :class:`Config` and
:class:`Context`.
"""

from .cmdlineparser import argument
from .config import Config, ConfigGroup, option
from .context import Context
from .tasks import BaseTask

__all__ = [
    'BaseTask', 'argument', 'Config', 'Context', 'ConfigGroup', 'option'
]
