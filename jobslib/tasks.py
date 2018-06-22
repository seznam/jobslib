"""
Module :module:`shelter.tasks` provides an ancestor class for writing tasks.
"""

import sys

from jobslib.cmdlineparser import argument

__all__ = ['BaseCommand', 'argument']


class BaseTask(object):
    """
    Ancestor for task. Inherit this class and adjust *name*, *help*
    and optionally *arguments* attributes and override *task()* method.
    *arguments* is a :class:`tuple` containing command line arguments
    for task. Constructor argument *config* is an instance of the
    :class:`jobslib.config.Config`.

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
    Task name..
    """

    help = ''
    """
    Task description.
    """

    arguments = ()
    """
    Task command line arguments.
    """

    def __init__(self, config):
        self.context = None  # TODO: config.context_class.from_config(config)
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.initialize()

    def __call__(self):
        raise NotImplementedError

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
