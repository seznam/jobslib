
import sys

from jobslib import BaseTask, argument, Config, option


CONFIG_CLASS = 'example.helloworld.HelloWorldConfig'


class HelloWorldConfig(Config):

    @option
    def yourname(self):
        return self._args_parser.yourname


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
