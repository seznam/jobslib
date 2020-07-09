
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


.. py:data:: settings.LIVENESS

Default: ``{'backend': 'jobslib.liveness.dummy.DummyLiveness'}``

Liveness implementation class. Value must be Python's module path
``[package.[submodule.]]module.ClassName``. If value is not defined,
default value ``jobslib.liveness.dummy.DummyLiveness`` is used.

.. code-block:: python

    LIVENESS = {
        'backend': 'jobslib.liveness.consul.ConsulLiveness',
        'options': {
            'key': 'jobs/example/liveness',
        },
    }


.. py:data:: settings.METRICS

Default: ``{'backend': 'jobslib.metrics.dummy.DummyMetrics'}``

Metrics implementation class. Value must be Python's module path
``[package.[submodule.]]module.ClassName``. If value is not defined,
default value ``jobslib.metrics.dummy.DummyMetrics`` is used.

.. code-block:: python

    METRICS = {
        'backend': 'jobslib.metrics.influxdb.InfluxDBMetrics',
    }


.. py:data:: settings.ONE_INSTANCE

Default: no default value, required option

One instance lock implementation class. Value must be Python's
module path ``[package.[submodule.]]module.ClassName``. For
development purposes you can use ``jobslib.oneinstance.dummy.DummyLock``.
If :option:`--disable-one-instance` argument is passed, dummy lock will
be forced.

.. code-block:: python

    ONE_INSTANCE = {
        'backend': 'jobslib.oneinstance.consul.ConsulLock',
        'options': {
            'key': 'jobs/example/oneinstance/lock',
            'ttl': 30,
        }
    }


.. py:data:: settings.CONSUL

Default: ``{}`` (empty :class:`!dict`)

Configuration of the connection arguments to HashiCorp Consul.

.. code-block:: python

    CONSUL = {
        'host': 'hostname',
        'port': 8500,
        'timeout': 1.0,
    }


.. py:data:: settings.INFLUXDB

Default: ``{}`` (empty :class:`!dict`)

Configuration of the connection arguments to InfluxDb.

.. code-block:: python

    INFLUXDB = {
        'host': 'hostname',
        'port': 8086,
        'username': 'root',
        'password': 'root',
        'database': 'dbname',
    }


.. py:data:: settings.LOGGING

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
             metrics

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
