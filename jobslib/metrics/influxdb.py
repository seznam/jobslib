"""
Module :mod:`jobslib.metrics.influxdb` provides :class:`InfluxDBMetrics`
writer.
"""

import datetime
import logging
import time

from . import BaseMetrics

__all__ = ['InfluxDBMetrics']

logger = logging.getLogger(__name__)


class InfluxDBMetrics(BaseMetrics):
    """
    InfluxDB metrics implementation.

    For use of :class:`InfluxDBMetrics` write into :mod:`settings`:

    .. code-block:: python

        INFLUXDB = {
            'host': 'hostname',
            'port': 8086,
            'username': 'root',
            'password': 'root',
            'database': 'dbname',
        }

        METRICS = {
            'backend': 'jobslib.metrics.influxdb.InfluxDBMetrics',
        }
    """

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
            self.context.influxdb.write_points(points)
        except Exception:
            logger.exception('Push monitoring metrics into InfluxDb failed')
