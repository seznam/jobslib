
import sys
import collections

from unittest import mock

import pytest

from jobslib import BaseTask
from jobslib.config import Config, ConfigGroup, option
from jobslib.context import Context
from jobslib.liveness.consul import ConsulLiveness
from jobslib.metrics.influxdb import InfluxDBMetrics
from jobslib.oneinstance.consul import ConsulLock


class TaskModuleMockClass:
    class TaskClassMockClass(BaseTask):
        pass


sys.modules["mock_task"] = TaskModuleMockClass


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


@pytest.mark.parametrize(
    'run_interval, sleep_interval',
    [(None, None), (300, None), (None, 300)]
)
def test_config(run_interval, sleep_interval):

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

        METRICS = {
            'backend': 'jobslib.metrics.influxdb.InfluxDBMetrics',
        }

        CONSUL = {
            'host': '192.168.1.100',
            'port': 1234,
            'timeout': 5.0,
        }

        INFLUXDB = {
            'host': '192.168.1.101',
            'port': 5678,
            'username': 'root',
            'password': 'secret',
            'database': 'testdb',
        }

    ArgsParser = collections.namedtuple('ArgsParser', [
        'disable_one_instance', 'run_once', 'run_interval',
        'sleep_interval', 'keep_lock', 'task_cls'])

    args_parser = ArgsParser(
        disable_one_instance=False, run_once=True, run_interval=run_interval,
        sleep_interval=sleep_interval, keep_lock=True,
        task_cls='mock_task.TaskClassMockClass')

    config = Config(settings, args_parser, mock.Mock())

    assert config.logging == settings.LOGGING
    assert config.context_class is Context
    assert config.one_instance.backend is ConsulLock
    assert config.one_instance.options.key == 'jobs/example/oneinstance/lock'
    assert config.one_instance.options.ttl == 30
    assert config.run_once is True
    assert config.sleep_interval == (
        sleep_interval if sleep_interval is not None else 0)
    assert config.run_interval == (
        run_interval if run_interval is not None else 0)
    assert config.keep_lock is True
    assert config.liveness.backend is ConsulLiveness
    assert config.liveness.options.key == 'jobs/example/oneinstance/liveness'
    assert config.metrics.backend is InfluxDBMetrics
    assert config.consul.scheme == 'http'
    assert config.consul.host == '192.168.1.100'
    assert config.consul.port == 1234
    assert config.consul.timeout == 5.0
    assert config.influxdb.host == '192.168.1.101'
    assert config.influxdb.port == 5678
    assert config.influxdb.username == 'root'
    assert config.influxdb.password == 'secret'
    assert config.influxdb.database == 'testdb'
