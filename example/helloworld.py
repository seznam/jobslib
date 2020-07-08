
import sys

from jobslib import BaseTask, argument, Config, option

# settings --------------------------------------------------------------------

RUN_ONCE = True

CONFIG_CLASS = 'example.helloworld.HelloWorldConfig'

ONE_INSTANCE = {
    'backend': 'jobslib.oneinstance.dummy.DummyLock',
}


# config ----------------------------------------------------------------------

class HelloWorldConfig(Config):

    @option
    def yourname(self):
        return self._args_parser.yourname


# task ------------------------------------------------------------------------

class HelloWorld(BaseTask):

    name = 'helloworld'
    description = 'prints welcome message'
    arguments = (
        argument(
            '-n', '--name', action='store', dest='yourname',
            default='World', help='your name'),
    )

    def task(self):
        sys.stdout.write('Hello {}!\n'.format(self.context.config.yourname))
        sys.stdout.flush()
