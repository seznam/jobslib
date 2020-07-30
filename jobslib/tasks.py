"""
Module :mod:`shelter.tasks` provides an ancestor class for writing tasks.
"""

import enum
import logging
import signal
import sys
import time

from .exceptions import Terminate
from .oneinstance import OneInstanceWatchdogError
from .time import get_current_time

__all__ = ['BaseTask']


class JobStatus(enum.Enum):
    UNKNOWN = 'unknown'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    PENDING = 'pending'
    INTERRUPTED = 'interrupted'
    KILLED = 'killed'


class BaseTask(object):
    """
    Ancestor for task. Inherit this class and adjust :attr:`name`,
    :attr:`description` and optionally :attr:`arguments` attributes and
    override :meth:`task` method. Constructor's argument *config* is
    instance of the :class:`~jobslib.Config` (or descendant).

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
            description = 'prints hello world'
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
    Task name.
    """

    description = ''
    """
    Task description.
    """

    arguments = ()
    """
    Task command line arguments. :class:`tuple` containing command line
    arguments. Each argument is defined using :func:`~jobslib.argument`
    function.

    .. code-block:: python

        arguments = (
            argument('-f', '--file', action='store', dest='filename'),
        )
    """

    def __init__(self, config):
        self.context = config.context_class.from_config(config)
        self.logger = logging.getLogger(
            '{}.{}'.format(self.__class__.__module__, self.__class__.__name__))
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
            last_successful_run_timestamp = None
            job_status = JobStatus.UNKNOWN
            keep_lock = self.context.config.keep_lock

            try:
                if lock.acquire():
                    terminate = False
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
                    except Terminate:
                        terminate = True
                        raise
                    finally:
                        if (keep_lock
                                and not self.context.config.run_once
                                and not terminate):
                            lock.refresh()
                        else:
                            lock.release()

                    liveness.write()
                    job_status = JobStatus.SUCCEEDED
                    last_successful_run_timestamp = get_current_time()
                else:
                    lock_owner_info = lock.get_lock_owner_info()
                    if lock_owner_info:
                        self.logger.info(
                            "Can't acquire lock (lock owner is %s, "
                            "locked at %s UTC)", lock_owner_info.get('fqdn'),
                            lock_owner_info.get('time_utc'))
                    else:
                        self.logger.info("Can't acquire lock")
                    keep_lock = False
                    job_status = JobStatus.PENDING
            except OneInstanceWatchdogError:
                dur = time.time() - start_time
                self.logger.exception("Lock has expired after %d seconds", dur)
                job_status = JobStatus.INTERRUPTED
                if self.context.config.run_once:
                    raise
            except Terminate:
                self.logger.warning("Task has been terminated")
                job_status = JobStatus.KILLED
                raise
            except Exception:
                self.logger.exception("%s task failed", self.name)
                job_status = JobStatus.FAILED
                if self.context.config.run_once:
                    raise
            finally:
                metrics_data = {
                    'job_duration_seconds': {
                        'value': time.time() - start_time,
                        'tags': {
                            'status': job_status.value,
                            'type': 'task',
                        },
                    },
                }
                if last_successful_run_timestamp:
                    metrics_data['last_successful_run_timestamp'] = {
                        'value': get_current_time(),
                    }
                metrics.push(metrics_data)

            if self.context.config.run_once:
                break

            if self.context.config.sleep_interval:
                sleep_time = self.context.config.sleep_interval
            else:
                next_run = start_time + self.context.config.run_interval
                sleep_time = max(next_run - time.time(), 0)

            if keep_lock:
                self.logger.info(
                    "Sleep for %d seconds, lock is kept", sleep_time)

                sleep_start_time = time.time()
                sleep_stop_time = sleep_start_time + sleep_time
                while time.time() < sleep_stop_time:
                    lock.refresh()
                    time.sleep(1)
                lock.release()
            else:
                self.logger.info(
                    "Sleep for %d seconds", sleep_time)

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

    def extend_lock(self):
        """
        Refresh existing lock. Return :data:`!True` if lock has been
        successfuly refreshed, otherwise return :data:`!False`. See
        :mod:`jobslib.oneinstance`.
        """
        return self.context.one_instance_lock.refresh()


class _Task(BaseTask):
    """
    Ancestor for internal task. Only for internal usage.
    """

    def __call__(self):
        self.context.config._configure_logging()
        self.task()
