import logging
import os

from ..objectvalidator import option
from . import BaseMetrics
from ..config import ConfigGroup

from influxdb_wrapper import DoporucovaniInfluxDBCLient

__all__ = ['InfluxDBMetrics']


class InfluxDBMetrics(BaseMetrics):
    """
    InfluxDB metrics implementation.

    For use of :class:`InfluxDBMetrics` write into **settings**:

    .. code-block:: python

        METRICS = {
            'backend': 'jobslib.metrics.influxdb.InfluxDBMetrics',
            'options': {
                'host': '127.0.0.1',
                'port': 8086,
                'username': 'root',
                'password': 'root',
                'database': 'dbname'
            }
        }

    """

    class OptionsConfig(ConfigGroup):
        @option(required=True, attrtype=str)
        def host(self):
            """
            InfluxDB host
            """
            host = os.environ.get('JOBSLIB_METRICS_INFLUXDB_HOST')
            if host:
                return host
            return self._settings.get('host', '127.0.0.1')

        @option(attrtype=int)
        def port(self):
            """
            InfluxDB port
            """
            port = os.environ.get('JOBSLIB_METRICS_INFLUXDB_PORT')
            if port:
                return port
            return self._settings.get('port', 8086)

        @option(required=True, attrtype=str)
        def username(self):
            """
            InfluxDB username
            """
            username = os.environ.get('JOBSLIB_METRICS_INFLUXDB_USERNAME')
            if username:
                return username
            return self._settings.get('username', "root")

        @option(required=True, attrtype=str)
        def password(self):
            """
            InfluxDB password
            """
            password = os.environ.get('JOBSLIB_METRICS_INFLUXDB_PASSWORD')
            if password:
                return password
            return self._settings.get('password', "root")

        @option(required=True, attrtype=str)
        def database(self):
            """
            InfluxDB database
            """
            database = os.environ.get('JOBSLIB_METRICS_INFLUXDB_DBNAME')
            if database:
                return database
            return self._settings.get('database', "dbname")

    def __init__(self, context, options):
        super().__init__(context, options)
        kwargs = {
            k: v for k, v in options.as_kwargs.items()
            if v is not None
        }

        self._client = DoporucovaniInfluxDBCLient(app=context.config.task_class.name, **kwargs)

    def push_monitoring_metrics(self, metrics, timestamp=None):
        self._client.push_monitoring_metrics(metrics=metrics, timestamp=timestamp)

    def push_monitoring_metrics_with_tags(self, metrics, timestamp=None):
        self._client.push_monitoring_metrics_with_tags(metrics=metrics, timestamp=timestamp)
