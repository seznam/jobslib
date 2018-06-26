"""
Module :module:`shelter.tasks` provides an ancestor class for writing tasks.
"""

import socket
import sys

from .cmdlineparser import argument

__all__ = ['BaseCommand', 'argument']


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
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.initialize()

    def __call__(self):
        self.context.config.configure_logging()

        if self.context.config.one_instance:
            session_id = self.context.consul.session.create(
                ttl=self.context.config.one_instance_ttl)
        else:
            session_id = None

        try:
            # TODO: one instance lock
            self.task()
        finally:
            if session_id:
                self.context.consul.Session.destroy(session_id)

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
