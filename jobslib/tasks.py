"""
Module :module:`shelter.tasks` provides an ancestor class for writing tasks.
"""

import logging
import signal
import sys
import time

from .exceptions import Terminate
from .oneinstance import OneInstanceWatchdogError
from .metrics import BaseMetrics
from .time import get_current_time

__all__ = ['BaseTask']


class BaseTask(object):
    """
    Ancestor for task. Inherit this class and adjust :attr:`name`,
    :attr:`help` and optionally :attr:`arguments` attributes and override
    :meth:`task` method. Constructor's argument *config* is instance of
    the :class:`~jobslib.Config` (or descendant).

    There are several attributes which are set during initialization.
    :attr:`context` is instance of the :class:`~jobslib.Context`.
    Configuration is available on context as :attr:`Context.config`
    attribute. :attr:`logger` is instance of the :class:`logging.Logger`.
    :attr:`stdout` and :attr:`stderr` are file-like objects for standard
    output and error.

    .. code-block:: python

        from jobslib import BaseTask, argument

        class HelloWorldTask(BaseTask):

            name = 'hello'
            help = 'prints hello world'
            arguments = (
                argument('--to-stderr', action='strore_true', default=False,
                         help='use stderr instead of stdout'),
            )

            def task(self):
                self.logger.info("Hello world")
                if self.context.config.to_stderr:
                    self.stderr("Hello world\\n")
                    self.stderr.flush()
                else:
                    self.stdout("Hello world\\n")
                    self.stdout.flush()
    """

    name = ''
    """
    Task's name.
    """

    help = ''
    """
    Task's description.
    """

    arguments = ()
    """
    Task's command line arguments. :class:`tuple` containing command line
    arguments. Each argument is defined using :func:`~jobslib.argument`
    function.

    .. code-block:: python

        arguments = (
            argument('-f', '--file', action='store', dest='filename'),
        )
    """

    def __init__(self, config):
        self.context = config.context_class.from_config(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.initialize()

    def __call__(self):
        self.context.config._configure_logging()

        lock = self.context.one_instance_lock
        liveness = self.context.liveness
        metrics = self.context.metrics

        while 1:
            start_time = time.time()

            try:
                if lock.acquire():
                    try:
                        self.logger.info("Run task")

                        signal.signal(signal.SIGTERM, self.terminate_process)
                        signal.signal(signal.SIGINT, self.terminate_process)
                        try:
                            self.task()
                        finally:
                            signal.signal(signal.SIGTERM, signal.SIG_DFL)
                            signal.signal(signal.SIGINT, signal.SIG_DFL)

                        self.logger.info("Task done")
                    finally:
                        lock.release()

                    liveness.write()
                    duration = time.time() - start_time
                    metrics.job_duration_seconds(
                        status=BaseMetrics.JOB_STATUS_SUCCEEDED,
                        duration=duration)
                    metrics.last_successful_run_timestamp(
                        timestamp=get_current_time())
                else:
                    self.logger.info(
                        "Can't acquire lock (lock owner is %s)",
                        lock.get_lock_owner_info())

                    duration = time.time() - start_time
                    metrics.job_duration_seconds(
                        status=BaseMetrics.JOB_STATUS_PENDING,
                        duration=duration)
            except OneInstanceWatchdogError:
                self.logger.exception("Task has been killed by watchdog!")
                duration = time.time() - start_time
                metrics.job_duration_seconds(
                    status=BaseMetrics.JOB_STATUS_INTERRUPTED,
                    duration=duration)
            except Terminate:
                self.logger.warning("Task has been terminated!")
                duration = time.time() - start_time
                metrics.job_duration_seconds(
                    status=BaseMetrics.JOB_STATUS_INTERRUPTED,
                    duration=duration)
                break
            except Exception:
                duration = time.time() - start_time
                self.logger.exception("%s task failed", self.name)
                metrics.job_duration_seconds(
                    status=BaseMetrics.JOB_STATUS_FAILED,
                    duration=duration)

            if self.context.config.run_once:
                break

            if self.context.config.sleep_interval:
                sleep_time = self.context.config.sleep_interval
            else:
                next_run = start_time + self.context.config.run_interval
                sleep_time = max(next_run - time.time(), 0)
            self.logger.info("Sleep for %d seconds", sleep_time)
            time.sleep(sleep_time)

    def initialize(self):
        """
        Initialize instance attributes. You can override this method in
        the subclasses.
        """
        pass

    def task(self):
        """
        Task body, override this method.
        """
        raise NotImplementedError

    def terminate_process(self, unused_signal_number, unused_frame):
        raise Terminate


class _Task(BaseTask):
    """
    Ancestor for internal task. Only for internal usage.
    """

    def __call__(self):
        self.context.config._configure_logging()
        self.task()
