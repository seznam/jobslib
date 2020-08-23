"""
Module :mod:`jobslib.config` provides base class which encapsulates
configuration.
"""

import json
import logging.config
import os

from objectvalidator import option, OptionsContainer

from .context import Context
from .imports import import_object
from .logging import BASE_LOGGING

__all__ = ['Config', 'ConfigGroup']


class ConfigGroup(OptionsContainer):
    """
    Container for configuration. During initialization values from all
    methods decorated by :class:`option` decorator are read. So if class
    is successfuly initialized, all options are validated and cached.
    """

    def initialize(self, *args, **unused_kwargs):
        """
        Initialize instance attributes. You can override this method in
        the subclasses.
        """
        self._settings, self._args_parser = args

    @property
    def as_kwargs(self):
        """
        Return all options as a :class:`dict`.
        """
        return {
            name: getattr(self, name)
            for name in option.get_option_names(self)
        }


class Config(OptionsContainer):
    """
    Class which encapsulates configuration. It joins configuration values
    from :mod:`settings` module and from command line. :mod:`settings` is
    Python module defined by either :envvar:`JOBSLIB_SETTINGS_MODULE`
    environment variable or :option:`-s/--settings` command line argument.
    *args_parser* is instance of the :class:`argparse.Namespace`. Both values
    are available on class, *settings* as a :attr:`_settings` attribute and
    *args_parser* as an :attr:`_args_parser` attribute.

    Configuration options are placed on class as methods decorated by
    :class:`option` decorator. During class initialization all decorated
    methods are read, so it implies values validation a caching. If you want
    nested configurations options, use :class:`ConfigGroup`. Reading value of
    the nested class during initialization implies the same mechanism, so all
    configuration will be validated and cached recursively.

    Example of the custom :class:`Config` class:

    .. code-block:: python

        import os

        from jobslib import Config, ConfigGroup, option

        class AuthServiceConfig(ConfigGroup):

            @option(required=True, attrtype=str)
            def uri(self):
                # First try reading value from command line
                uri = self._args_parser.auth_servise_uri
                if uri:
                    return uri

                # Then try reading value from environment variable
                uri = os.environ.get('MYAPP_AUTH_SERVICE_URI')
                if uri is not None:
                    return uri

                # Finally try reading value from settings
                return self._settings['uri']

        class MyAppConfig(Config):

            @option
            def auth_service(self):
                return AuthServiceConfig(
                    self._settings['AUTH_SERVICE'], self._args_parser)

    And write into :mod:`settings` module:

    .. code-block:: python

        CONFIG_CLASS = 'myapp.config.MyAppConfig'

        AUTH_SERVICE = {
            'uri': 'http://example.com/api/v1/auth',
        }

    Configuration options are available on the :class:`Config` as
    attributes. If any configuration value is not valid, exception will
    be raised and instance will not be created.

    .. code-block:: python

        >>> context.config.auth_service.uri
        'http://example.com/api/v1/auth'
    """

    def __init__(self, settings, args_parser, task_cls):
        self._settings = settings
        self._args_parser = args_parser
        self._task_cls = task_cls
        super().__init__()

    def __repr__(self):
        return "<{}.{}: {:#x}>".format(
            self.__class__.__module__, self.__class__.__name__, id(self)
        )

    def initialize(self, *args, **kwargs):
        """
        Initialize instance attributes. You can override this method in
        the subclasses.
        """
        pass

    def _configure_logging(self):
        """
        Configure Python's logging according to configuration stored in the
        :attr:`logging` property.
        """
        logging.config.dictConfig(self.logging)

    @option
    def logging(self):
        """
        Python's logging configuration or :data:`BASE_LOGGING` if value is
        not defined. :data:`BASE_LOGGING` allowes :data:`~logging.INFO`
        and higher leveled messages and forwards them onto console. Format
        is :func:`logging.config.dictConfig`.
        """
        logging_cfg = os.environ.get('JOBSLIB_LOGGING')
        if logging_cfg:
            return json.loads(logging_cfg)
        return getattr(self._settings, 'LOGGING', BASE_LOGGING)

    @option
    def context_class(self):
        """
        Context class, either :class:`~jobslib.Context` class or subclass.
        """
        context_cls_name = getattr(self._settings, 'CONTEXT_CLASS', '')
        if context_cls_name:
            context_class = import_object(context_cls_name)
        else:
            context_class = Context
        return context_class

    @option
    def task_class(self):
        """
        Task class, subclass of the :class:`~jobslib.BaseTask`.
        """
        return self._task_cls

    @option
    def run_once(self):
        """
        :class:`!bool` that indicates that task will be run only once.
        """
        if self._args_parser.run_once is not None:
            return self._args_parser.run_once
        run_once = os.environ.get('JOBSLIB_RUN_ONCE')
        if run_once:
            return bool(int(run_once))
        return getattr(self._settings, 'RUN_ONCE', False)

    @option(attrtype=int)
    def sleep_interval(self):
        """
        Sleep interval in seconds after task is done.
        """
        if self._args_parser.sleep_interval is not None:
            sleep_interval = self._args_parser.sleep_interval
        else:
            sleep_interval = os.environ.get('JOBSLIB_SLEEP_INTERVAL')
            if sleep_interval:
                sleep_interval = int(sleep_interval)
            else:
                sleep_interval = getattr(self._settings, 'SLEEP_INTERVAL', 0)
        if sleep_interval < 0:
            raise ValueError('Run interval may not be less than 0')
        return sleep_interval

    @option(attrtype=int)
    def run_interval(self):
        """
        Run interval in seconds. If task is run longer than this interval,
        next loop is run imediately after task is done.
        """
        if self._args_parser.run_interval is not None:
            run_interval = self._args_parser.run_interval
        else:
            run_interval = os.environ.get('JOBSLIB_RUN_INTERVAL')
            if run_interval:
                run_interval = int(run_interval)
            else:
                run_interval = getattr(self._settings, 'RUN_INTERVAL', 0)
        if run_interval < 0:
            raise ValueError('Run interval may not be less than 0')
        return run_interval

    @option
    def keep_lock(self):
        """
        :class:`!bool` that indicates that lock will be kept during sleeping.
        """
        if self._args_parser.keep_lock is not None:
            return self._args_parser.keep_lock
        keep_lock = os.environ.get('JOBSLIB_KEEP_LOCK')
        if keep_lock:
            return bool(int(keep_lock))
        return getattr(self._settings, 'KEEP_LOCK', False)

    @option
    def one_instance(self):
        """
        Configuration of the one instance lock. Instance of the
        :class:`OneInstanceConfig`.
        """
        return OneInstanceConfig(
            getattr(self._settings, 'ONE_INSTANCE', {}), self._args_parser)

    @option
    def liveness(self):
        """
        Configuration of the health state writer. Instance of the
        :class:`LivenessConfig`.
        """
        return LivenessConfig(
            getattr(self._settings, 'LIVENESS', {}), self._args_parser)

    @option
    def metrics(self):
        return MetricsConfig(
            getattr(self._settings, 'METRICS', {}), self._args_parser)


class OneInstanceConfig(ConfigGroup):
    """
    Configuration of the one instance lock.
    """

    @option
    def backend(self):
        """
        One instance lock implementation class. Value must be Python's module
        path ``[package.[submodule.]]module.ClassName``. For development
        purposes you can use ``jobslib.oneinstance.dummy.DummyLock``. If
        ``--disable-one-instance`` argument is passed,
        :class:`jobslib.oneinstance.dummy.DummyLock` will be forced.
        """
        if self._args_parser.disable_one_instance:
            cls_name = 'jobslib.oneinstance.dummy.DummyLock'
        else:
            cls_name = os.environ.get('JOBSLIB_ONE_INSTANCE_BACKEND')
            if not cls_name:
                cls_name = self._settings['backend']
        return import_object(cls_name)

    @option
    def options(self):
        """
        Constructor's arguments of the one instance implementation class.
        It depends on :meth:`backend` attribute.
        """
        return self.backend.OptionsConfig(
            self._settings.get('options', {}), self._args_parser)


class LivenessConfig(ConfigGroup):
    """
    Configuration of the liveness writer.
    """

    @option
    def backend(self):
        """
        Liveness implementation class. If value is not defined, default
        value ``jobslib.liveness.dummy.DummyLiveness`` is used.
        """
        cls_name = os.environ.get('JOBSLIB_LIVENESS_BACKEND')
        if not cls_name:
            cls_name = self._settings.get(
                'backend', 'jobslib.liveness.dummy.DummyLiveness')
        return import_object(cls_name)

    @option
    def options(self):
        """
        Constructor's arguments of the liveness implementation class.
        """
        return self.backend.OptionsConfig(
            self._settings.get('options', {}), self._args_parser)


class MetricsConfig(ConfigGroup):
    """
    Configuration of the metrics writer.
    """

    @option
    def backend(self):
        """
        Metrics implementation class. If value is not defined, default
        value ``jobslib.metrics.dummy.DummyMetrics`` is used.
        """
        cls_name = os.environ.get('JOBSLIB_METRICS_BACKEND')
        if not cls_name:
            cls_name = self._settings.get(
                'backend', 'jobslib.metrics.dummy.DummyMetrics')
        return import_object(cls_name)

    @option
    def options(self):
        """
        Constructor's arguments of the metrics implementation class.
        """
        return self.backend.OptionsConfig(
            self._settings.get('options', {}), self._args_parser)


class RetryConfigMixin(object):

    @option(required=True, attrtype=int)
    def retry_max_attempts(self):
        """
        Number of attempts when some operation failes. Default is 0.
        """
        env_name = "{}{}".format(self.retry_env_prefix, 'RETRY_MAX_ATTEMPTS')
        if env_name in os.environ:
            retry_max_attempts = int(os.environ.get(env_name))
        else:
            retry_max_attempts = self._settings.get('retry_max_attempts', 0)
        return retry_max_attempts

    @option(required=True, attrtype=int)
    def retry_wait_multiplier(self):
        """
        Wait ``2^x * multiplier`` milliseconds between each retry. Default
        is 50. So waits between each retries will be 0.1 sec, 0.2 sec,
        0.4 sec, 0.8 sec, 1.6 sec, 3.2 sec, ...
        """
        env_name = "{}{}".format(
            self.retry_env_prefix, 'RETRY_WAIT_MULTIPLIER')
        if env_name in os.environ:
            multiplier = int(os.environ.get(env_name))
        else:
            multiplier = self._settings.get('retry_wait_multiplier', 50)
        return multiplier
