
Reference manual
================

``Settings`` – basic configuration of your application
------------------------------------------------------

.. py:module:: settings

Basic configuration of your task is placed in :mod:`!settings` module.
It is common Python module, which is passed into Jobslib using either
:option:`-s/--settings` command line argument or
:envvar:`JOBSLIB_SETTINGS_MODULE` environment variable. It contains a few
options for basic application settings.

.. code-block:: console

    $ # Pass settings module using -s argument
    $ runjob -s myapp.settings myapp.task.HelloWorld

    $ # Pass settings module using environment variable
    $ JOBSLIB_SETTINGS_MODULE=myapp.settings runjob myapp.task.HelloWorld

List of basic settings
^^^^^^^^^^^^^^^^^^^^^^

Some options try obtainig values from several sources. First from command
line argument, then from environment variable and finally from :mod:`settings`
module. Environment variables are ``JOBSLIB_`` prefixed.

.. py:data:: settings.CONFIG_CLASS

Default: ``'jobslib.Config'``

Application configuration class. Jobslib provides default
:class:`~jobslib.Config` class, which converts basic options from
:mod:`settings` module to instance attributes.

.. code-block:: python

    CONFIG_CLASS = 'myapplicaton.config.Config'


.. py:data:: settings.CONTEXT_CLASS

Default: ``'jobslib.Context'``

Application context class. Context is a container for shared
resources, e.g. database connection. Jobslib provides default
:class:`~jobslib.Context` class.

.. code-block:: python

    CONTEXT_CLASS = 'myapplicaton.context.Context'


.. option:: --run-once
.. envvar:: JOBSLIB_RUN_ONCE
.. py:data:: settings.RUN_ONCE

Default: ``False``

If set to :data:`!True`, indicates that task will be run only once.

.. code-block:: python

    RUN_ONCE = True


.. option:: --sleep-interval
.. envvar:: JOBSLIB_SLEEP_INTERVAL
.. py:data:: settings.SLEEP_INTERVAL

Default: ``0``

Sleep interval in seconds after task is done.

.. code-block:: python

    SLEEP_INTERVAL = 60.0


.. option:: --run-interval
.. envvar:: JOBSLIB_RUN_INTERVAL
.. py:data:: settings.RUN_INTERVAL

Default: ``0``

Run interval in seconds. If task is run longer than this interval,
next loop is run imediately after task is done.

.. code-block:: python

    RUN_INTERVAL = 60.0


.. option:: --keep-lock
.. envvar:: JOBSLIB_KEEP_LOCK
.. py:data:: settings.KEEP_LOCK

Default: ``False``

If set to :data:`!True`, indicates that lock will be kept during sleeping.

.. code-block:: python

    KEEP_LOCK = True

.. option:: --release-on-error
.. envvar:: JOBSLIB_RELEASE_ON_ERROR
.. py:data:: settings.RELEASE_ON_ERROR

Default: ``False``

If set to :data:`!True`, indicates that lock will be release on error (work with :option:`--keep-lock`).

.. code-block:: python

    KEEP_LOCK = True

.. py:data:: settings.LIVENESS

Default: ``{'backend': 'jobslib.liveness.dummy.DummyLiveness'}``

Liveness implementation class. Value must be :class:`!dict` containing
``backend`` key, which is Python's module path
``[package.[submodule.]]module.ClassName``. Or
:envvar:`JOBSLIB_LIVENESS_BACKEND` can be used. If value is not defined,
default value ``jobslib.liveness.dummy.DummyLiveness`` is used. See
:mod:`jobslib.oneinstance`.

.. code-block:: python

    LIVENESS = {
        'backend': 'jobslib.liveness.consul.ConsulLiveness',
        'options': {
            'host': 'hostname',
            'port': 8500,
            'timeout': 1.0,
            'key': 'jobs/example/liveness',
        },
    }


.. py:data:: settings.METRICS

Default: ``{'backend': 'jobslib.metrics.dummy.DummyMetrics'}``

Metrics implementation class. Value must be :class:`!dict` containing
``backend`` key, which is Python's module path
``[package.[submodule.]]module.ClassName``. Or
:envvar:`JOBSLIB_METRICS_BACKEND` can be used. If value is not defined,
default value ``jobslib.metrics.dummy.DummyMetrics`` is used. See
:mod:`jobslib.metrics`.

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


.. py:data:: settings.ONE_INSTANCE

Default: no default value, required option

One instance lock implementation class. Value must be :class:`!dict`
containing ``backend`` key, which is Python's module path
``[package.[submodule.]]module.ClassName``. Or
:envvar:`JOBSLIB_ONE_INSTANCE_BACKEND` can be used. For development
purposes you can use ``jobslib.oneinstance.dummy.DummyLock``. If
:option:`--disable-one-instance` argument is passed, dummy lock will
be forced. See :mod:`jobslib.oneinstance`.

.. code-block:: python

    ONE_INSTANCE = {
        'backend': 'jobslib.oneinstance.consul.ConsulLock',
        'options': {
            'host': 'hostname',
            'port': 8500,
            'timeout': 1.0,
            'key': 'jobs/example/oneinstance/lock',
            'ttl': 30,
        }
    }


.. py:data:: settings.LOGGING
.. envvar:: JOBSLIB_LOGGING

Default: root logger which logs to console:

Takes the logging configuration from a dictionary. See :mod:`logging.config`
module and :func:`logging.config.dictConfig` function documentation.

.. code-block:: python

    {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(asctime)s %(name)s %(levelname)s %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'NOTSET',
                'formatter': 'default',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    }

If logging configuration is passed in evironment variable, JSON object is
expected.

``Config`` – container for configuration
----------------------------------------

.. automodule:: jobslib.config

.. autofunction:: jobslib.argument

.. autoclass:: jobslib.Config
   :member-order: bysource
   :members: initialize,
             logging,
             context_class,
             task_class,
             run_once,
             sleep_interval,
             run_interval,
             keep_lock,
             one_instance,
             liveness,
             metrics,
             release_on_error

``Context`` – container for shared resources
--------------------------------------------

.. automodule:: jobslib.context

.. autoclass:: jobslib.Context
   :member-order: bysource
   :members: initialize,
             config,
             fqdn,
             one_instance_lock,
             liveness,
             metrics

``Task`` – class which encapsulates task
----------------------------------------

.. automodule:: jobslib.tasks

.. autoclass:: jobslib.BaseTask
   :member-order: bysource
   :members: name,
             description,
             arguments,
             task,
             extend_lock

``Liveness`` – informations about health state of the task
----------------------------------------------------------

.. automodule:: jobslib.liveness
   :members:

.. autoclass:: jobslib.liveness.dummy.DummyLiveness

.. autoclass:: jobslib.liveness.consul.ConsulLiveness
    :members: OptionsConfig

``Metrics`` – task metrics
--------------------------

.. automodule:: jobslib.metrics
   :members:

.. autoclass:: jobslib.metrics.dummy.DummyMetrics

.. autoclass:: jobslib.metrics.influxdb.InfluxDBMetrics

``One Instance Lock`` – only one running instance at the same time
------------------------------------------------------------------

.. automodule:: jobslib.oneinstance
   :members:

.. autoclass:: jobslib.oneinstance.dummy.DummyLock

.. autoclass:: jobslib.oneinstance.consul.ConsulLock
    :members: OptionsConfig
