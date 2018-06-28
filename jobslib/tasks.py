"""
Module :module:`shelter.tasks` provides an ancestor class for writing tasks.
"""

import logging
import sys
import time

__all__ = ['BaseCommand']


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

    logger = None

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

        counter = 0
        while 1:
            try:
                if self.context.one_instance_lock.acquire():
                    counter = 0
                    try:
                        self.task()
                    finally:
                        self.context.one_instance_lock.release()
                else:
                    counter += 1
                    if counter == 60:
                        self.logger.info("Can't acquire lock")
                        counter = 0
                time.sleep(1.0)
            except Exception:
                self.logger.exception("{} task failed".format(self.name))

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
