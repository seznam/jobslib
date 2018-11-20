from . import BaseMetrics

__all__ = ['DummyMetrics']


class DummyMetrics(BaseMetrics):
    """
        Dummy metrics implementation. Doesn't provide real functionality.
    It is useful for development or if it is not necessary metrics. For
    use of :class:`DummyMetrics` write into **settings**:

    .. code-block:: python

        LIVENESS = {
            'backend': 'jobslib.metrics.dummy.DummyMetrics',
        }
    """

    def push_monitoring_metrics(self, metrics, timestamp=None):
        pass

    def push_monitoring_metrics_with_tags(self, metrics, timestamp=None):
        pass
