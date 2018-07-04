
Welcome to jobslib's documentation!
===================================

jobslib
-------

.. automodule:: jobslib
   :members:

settings
--------

Example:

.. code-block:: python

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
