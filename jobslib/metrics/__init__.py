"""
Provides metrics API. Inherit this class and override abstract method
:meth:`push_monitoring_metrics`. Configuration options are defined in
:class:`OptionsConfig` class, which is :class:`~jobslib.ConfigGroup`
descendant.
"""

import abc

from jobslib import ConfigGroup

__all__ = ['BaseMetrics']


class BaseMetrics(abc.ABC):
    JOB_STATUS_SUCCEEDED = "succeeded"
    JOB_STATUS_FAILED = "failed"
    JOB_STATUS_INTERRUPTED = "interrupted"
    JOB_STATUS_PENDING = "pending"
    JOB_STATUS_IN_PROGRESS = "in_progress"
    JOB_STATUS_KILLED = "killed"
    JOB_STATUS_UNKNOWN = "unknown"

    class OptionsConfig(ConfigGroup):
        """
        Validation of the liveness configuration, see
        :class:`~jobslib.ConfigGroup`.
        """
        pass

    def __init__(self, context, options):
        self.context = context
        self.options = options

    @abc.abstractmethod
    def push_monitoring_metrics(self, metrics, timestamp=None):
        """Push metrics

        :param metrics: Key=name of metric, value is numeric value of metric
        :param timestamp: Timestamp
        """
        raise NotImplementedError

    @abc.abstractmethod
    def push_monitoring_metrics_with_tags(self, metrics, timestamp=None):
        """Push metrics with tags

        metrics = {
            "flow_velocity": {
                "value": 30.0,
                "tags": {
                    "tag_name1": "tag_value1",
                    "tag_name2": "tag_value2",
                }
            },
            "processed_requests": {
                "value": 5,
                "tags": {
                    "tag_name3": "tag_value3",
                }
            },
        }

        :param metrics: Metrics
        :param timestamp: Timestamp
        """
        raise NotImplementedError

    def errors_total(self, type, remote_app="", remote_app_method="", tags=None):
        """Errors metric.
        :param type: Error type as string
        :param remote_app: For errors on outgoing communication.
        :param remote_app_method: For errors on outgoing communication.
        :param tags: Additional tags for metric.
        """
        metric_name = "errors_total"

        t = dict(type=type,
                 remote_app=remote_app,
                 remote_app_method=remote_app_method)

        if tags is not None:
            t.update(tags)

        metric = {
            metric_name: dict(value=1, tags=t)
        }

        self.push_monitoring_metrics_with_tags(metrics=metric)

    def request_duration_seconds(self, endpoint, type, status_code, method, amount, tags=None):
        """Incoming request duration
        :param endpoint: Incoming endpoint (ex.: /foo for HTTP, foo.bar.baz for RPC)
        :param type: Request type (HTTP, XMLRPC, ...)
        :param status_code: Status code of request
        :param method: Request method (GET, POST, ..)
        :param amount: Duration.
        :param tags: Additional tags for metric.
        """
        metric_name = "request_duration_seconds"

        t = dict(type=type,
                 status_code=status_code,
                 endpoint=endpoint,
                 method=method)

        t.update(tags)

        metric = {
            metric_name: dict(value=amount, tags=t)
        }

        self.push_monitoring_metrics_with_tags(metrics=metric)

    def outgoing_request_duration_seconds(self, method, remote_app, endpoint, type, status_code, amount, tags=None):
        """Outgoing request duration
        :param method: Request method (GET, POST, ..)
        :param remote_app: Remote app name for DB host is fine as remote_app id.
        :param endpoint: Incoming endpoint (ex.: /foo for HTTP, foo.bar.baz for RPC)
        :param type: Request type (HTTP, XMLRPC, ...)
        :param status_code: Status code of request
        :param amount: Duration.
        :param tags: Additional tags for metric.
        """

        metric_name = "outgoing_request_duration_seconds"

        t = dict(method=method,
                 remote_app=remote_app,
                 type=type,
                 status_code=status_code,
                 endpoint=endpoint)

        if tags is not None:
            t.update(tags)

        metric = {
            metric_name: dict(value=amount, tags=t)
        }

        self.push_monitoring_metrics_with_tags(metrics=metric)

    def last_successful_run_timestamp(self, timestamp, tags=None):
        """Last succesful run timestamp.
        :param timestamp: Timestamp in UTC
        :param tags: Additional tags for metric.
        """
        metric_name = "last_successful_run_timestamp"

        metric_dict = dict(value=timestamp)

        if tags is not None:
            metric_dict.update(tags)

        metric = {
            metric_name: metric_dict
        }

        self.push_monitoring_metrics_with_tags(metrics=metric)

    def job_duration_seconds(self, duration, status, type="task", tags=None):
        """Job duration.
        :param duration: job duration in seconds.
        :param status: Job status one of JOB_STATUS_* "enum".
        :param type: Job type.
        :param tags: Additional tags for metric.
        """

        metric_name = "job_duration_seconds"

        t = dict(
            status=status,
            type=type
        )

        if tags is not None:
            t.update(tags)

        metric = {
            metric_name: dict(value=duration, tags=t)
        }

        self.push_monitoring_metrics_with_tags(metrics=metric)
