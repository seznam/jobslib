"""
Module :mod:`jobslib.metrics.influxdb` provides :class:`InfluxDBMetrics`
writer.
"""

import datetime
import logging
import os
import time

from influxdb.client import InfluxDBClient
from objectvalidator import option

from . import BaseMetrics
from ..config import ConfigGroup

__all__ = ['InfluxDBMetrics']

logger = logging.getLogger(__name__)


class InfluxDBMetrics(BaseMetrics):
    """
    InfluxDB metrics implementation.

    For use of :class:`InfluxDBMetrics` write into :mod:`settings`:

    .. code-block:: python

        METRICS = {
            'backend': 'jobslib.metrics.influxdb.InfluxDBMetrics',
            'options': {
                'host': 'hostname',
                'port': 8086,
                'username': 'root',
                'password': 'root',
                'database': 'dbname',
            },
        }

    Or use
    :envvar:`JOBSLIB_METRICS_INFLUXDB_HOST`,
    :envvar:`JOBSLIB_METRICS_INFLUXDB_PORT`,
    :envvar:`JOBSLIB_METRICS_INFLUXDB_USERNAME`,
    :envvar:`JOBSLIB_METRICS_INFLUXDB_PASSWORD` and
    :envvar:`JOBSLIB_METRICS_INFLUXDB_DBNAME` environment variables.
    """

    class OptionsConfig(ConfigGroup):
        """
        Consul liveness options.
        """

        @option(required=True, attrtype=str)
        def host(self):
            """
            InfluxDB host
            """
            host = os.environ.get('JOBSLIB_METRICS_INFLUXDB_HOST')
            if host:
                return host
            return self._settings.get('host', 'localhost')

        @option(attrtype=int)
        def port(self):
            """
            InfluxDB port
            """
            port = os.environ.get('JOBSLIB_METRICS_INFLUXDB_PORT')
            if port:
                return int(port)
            return self._settings.get('port', 8086)

        @option(required=True, attrtype=str)
        def username(self):
            """
            InfluxDB username
            """
            username = os.environ.get('JOBSLIB_METRICS_INFLUXDB_USERNAME')
            if username:
                return username
            return self._settings.get('username', 'root')

        @option(required=True, attrtype=str)
        def password(self):
            """
            InfluxDB password
            """
            password = os.environ.get('JOBSLIB_METRICS_INFLUXDB_PASSWORD')
            if password:
                return password
            return self._settings.get('password', 'root')

        @option(attrtype=str)
        def database(self):
            """
            InfluxDB database
            """
            database = os.environ.get('JOBSLIB_METRICS_INFLUXDB_DBNAME')
            if database:
                return database
            return self._settings['database']

    def __init__(self, context, options):
        super().__init__(context, options)
        self._influxdb = InfluxDBClient(
            host=self.options.host,
            port=self.options.port,
            username=self.options.username,
            password=self.options.password,
            database=self.options.database,
        )

    def push(self, metrics):
        current_dt = datetime.datetime.utcfromtimestamp(time.time())
        ts = current_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        task_name = self.context.config.task_class.name
        try:
            points = []
            for metric_name, metric_value in metrics.items():
                tags = {
                    'task': task_name,
                }
                for k, v in metric_value.get('tags', {}).items():
                    if k in tags:
                        raise Exception("Tag '{}' is reserved".format(k))
                    tags[k] = v
                metric = {
                    'measurement': metric_name,
                    'tags': tags,
                    'time': ts,
                    'fields': {
                        'value': metric_value['value'],
                    },
                }
                points.append(metric)
            self._influxdb.write_points(points)
        except Exception:
            logger.exception('Push monitoring metrics into InfluxDb failed')
