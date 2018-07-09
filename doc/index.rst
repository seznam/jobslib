
Welcome to jobslib's documentation!
===================================

jobslib
-------

.. automodule:: jobslib
   :members:

oneinstance lock
----------------

.. automodule:: jobslib.oneinstance
   :members:

.. autoclass:: jobslib.oneinstance.dummy.DummyLock

.. autoclass:: jobslib.oneinstance.consul.ConsulLock
    :members: OptionsConfig

liveness
--------

.. automodule:: jobslib.liveness
   :members:

.. autoclass:: jobslib.liveness.dummy.DummyLiveness

.. autoclass:: jobslib.liveness.consul.ConsulLiveness
    :members: OptionsConfig

settings
--------

Example:

.. code-block:: python

    CONFIG_CLASS = 'myapp.config.MyAppConfig'

    CONTEXT_CLASS = 'myapp.context.MyAppContext'

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
        'host': '127.0.0.1',
        'port': 8500,
    }

    LOGGING = {
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
