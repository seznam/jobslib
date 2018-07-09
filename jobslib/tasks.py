"""
Module :module:`shelter.tasks` provides an ancestor class for writing tasks.
"""

import logging
import sys
import time

from .oneinstance import OneInstanceWatchdogError

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
        while 1:
            try:
                if lock.acquire():
                    self.logger.info("Run task")
                    try:
                        self.task()
                    finally:
                        lock.release()
                    self.logger.info("Task done, write liveness")
                    liveness.write()
                else:
                    self.logger.info(
                        "Can't acquire lock (lock owner is %s)",
                        lock.get_lock_owner_info())
            except OneInstanceWatchdogError:
                self.logger.exception("Task has been killed by watchdog!")
            except Exception:
                self.logger.exception("%s task failed", self.name)

            if self.context.config.run_once:
                break
            self.logger.info(
                "Sleep for %d seconds", self.context.config.sleep_interval)
            time.sleep(self.context.config.sleep_interval)

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
