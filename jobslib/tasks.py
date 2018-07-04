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
    :meth:`help` and optionally :attr:`arguments` attributes and
    override :meth:`task` method. Constructor argument *config* is
    an instance of the :class:`jobslib.config.Config`.

    ::

        # application/tasks/hello.py

        from jobslib.tasks import BaseTask, argument

        class HelloCommand(BaseTask):

            name = 'hello'
            help = 'show hello'
            arguments = (
                argument('--name', dest='name', help='your name'),
            )

            def task(self):
                print("Hello %s" % self.args.name)
    """

    name = ''
    """
    Task name.
    """

    help = ''
    """
    Task description.
    """

    arguments = ()
    """
    Task command line arguments. :class:`tuple` containing command line
    arguments for task.

    ::

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
        self.context.config.configure_logging()

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
