
from jobslib.config import Config, ConfigGroup, option
from jobslib.context import Context
from jobslib.liveness.consul import ConsulLiveness
from jobslib.oneinstance.consul import ConsulLock


def test_config_group():

    class TestConfig(ConfigGroup):

        @option
        def baz(self):
            return 1

        @option
        def bar(self):
            return 2

    test_config = TestConfig(None, None)
    assert test_config.as_kwargs == {'baz': 1, 'bar': 2}


def test_config():

    class settings:

        LOGGING = {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': 'NOTSET',
                },
            },
            'root': {
                'handlers': ['console'],
                'level': 'INFO',
            },
        }

        CONTEXT_CLASS = 'jobslib.context.Context'

        ONE_INSTANCE = {
            'backend': 'jobslib.oneinstance.consul.ConsulLock',
            'options': {
                'key': 'jobs/example/oneinstance/lock',
                'ttl': 30,
            }
        }

        LIVENESS = {
            'backend': 'jobslib.liveness.consul.ConsulLiveness',
            'options': {
                'key': 'jobs/example/oneinstance/liveness',
            }
        }

        CONSUL = {
            'host': '192.168.1.100',
            'port': 1234,
        }

    class args_parser:

        one_instance = True
        run_once = True
        sleep_interval = 300

    config = Config(settings, args_parser)

    assert config.logging == settings.LOGGING
    assert config.context_class is Context
    assert config.one_instance.backend is ConsulLock
    assert config.one_instance.options.key == 'jobs/example/oneinstance/lock'
    assert config.one_instance.options.ttl == 30
    assert config.run_once is True
    assert config.sleep_interval == 300
    assert config.liveness.backend is ConsulLiveness
    assert config.liveness.options.key == 'jobs/example/oneinstance/liveness'
    assert config.consul.scheme == 'http'
    assert config.consul.host == '192.168.1.100'
    assert config.consul.port == 1234
