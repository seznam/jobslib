
Jobslib
=======

Introduction
------------

**Jobslib** is a library for launching tasks in parallel environment.
For example, you have two datacenters, in both is run server with some task,
however only one task may be active at one time. Main features are:

- Ancestor for class which holds configuration.
- Ancestor for container for shared resources, e.g. database connection.
- Ancestor for class with task.
- Configurable either from configuration file or from environmets variables.
- Liveness – for exporting informations about health state of the task.
  Includes implementation which uses `Consul <https://www.consul.io/>`_.
- Metrics – for exporting metrics. Includes implementation which uses
  `InfluxDB <https://www.influxdata.com/>`_.
- One Instance – lock which allowes only one running instance at the same time.
  Includes implementation which uses `Consul <https://www.consul.io/>`_.

Instalation and quick start
---------------------------

Installation from source code:

.. code-block:: console

    $ git clone https://github.com/seznam/jobslib.git
    $ cd jobslib
    $ python setup.py install

Installation from PyPi:

.. code-block:: console

    $ pip install jobslib

`Tox <https://tox.readthedocs.io/en/latest/>`_ is used for testing:

.. code-block:: console

    $ git clone https://github.com/seznam/jobslib.git
    $ cd jobslib
    $ pip install tox
    $ tox --skip-missing-interpreters

Task is launched from command line using :command:`runjob` command:

.. code-block:: console

    $ runjob [-s SETTINGS] [--disable-one-instance] [--run-once]
             [--sleep-interval SLEEP_INTERVAL] [--run-interval RUN_INTERVAL]
             [--keep-lock]
             task_cls

    $ # Pass settings module using -s argument
    $ runjob -s myapp.settings myapp.task.HelloWorld --run-once

    $ # Pass settings module using environment variable
    $ export JOBSLIB_SETTINGS_MODULE="myapp.settings"
    $ runjob myapp.task.HelloWorld --run-once

Task is normally run in infinite loop, delay in seconds between individual
launches is controlled by either :option:`--sleep-interval` or
:option:`--run-interval` argument. :option:`--sleep-interval` is interval in
seconds, which is used to sleep after task is done. :option:`--run-interval`
tells that task is run every run interval seconds. Both arguments may not be
used together. :option:`--keep-lock` argument causes that lock will be kept
during sleeping, it is useful when you have several machines and you want to
keep the task still on the same machine. If you don't want to launch task
forever, use ``--run-once`` argument. Library provides locking mechanism for
launching tasks on several machines and only one instance at one time may be
launched. If you don't want this locking, use :option:`--disable-one-instance`
argument. All these options can be set in :mod:`!settings` module. Optional
argument :option:`-s/--settings` defines Python module where configuration
is stored. Or you can pass settings module using
:envvar:`JOBSLIB_SETTINGS_MODULE`.

During task initialization instances of the :class:`jobslib.Config` and
:class:`jobslib.Context` classes are created. You can define your own classes
in the :mod:`!settings` module. :class:`jobslib.Config` is a container which
holds configuration. :class:`jobslib.Context` is a container which holds
resources which are necessary for your task, for example database connection.
Finally, when both classes are successfuly initialized, instance of the task
(subclass of the :class:`jobslib.BaseTask` passed as a :option:`task_cls`
argument) is created and launched.

If you want to write your own task, inherit :class:`jobslib.BaseTask` class
and override :meth:`jobslib.BaseTask.task` method. According to your
requirements inherit and override :class:`jobslib.Config` and/or
:class:`jobslib.Context` and set :mod:`!settings` module:

.. code-block:: python
    :caption: helloworld/settings.py

    ONE_INSTANCE = {
        'backend': 'jobslib.oneinstance.dummy.DummyLock',
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

.. code-block:: python
    :caption: helloworld/task.py

    from jobslib import BaseTask

    class HelloWorld(BaseTask):

    name = 'helloworld'
    description = 'prints hello world'

    def task(self):
        sys.stdout.write('Hello World!\n')
        sys.stdout.flush()

.. code-block:: console

    $ runjob -s helloworld.settings --run-once helloworld.task.HelloWorld
    2020-07-03 14:53:25 helloworld.task.HelloWorld INFO Run task
    Hello World!
    2020-07-03 14:53:25 helloworld.task.HelloWorld INFO Task done

Reference manual
----------------

.. toctree::
   :maxdepth: 2

   reference-manual

Source code and license
-----------------------

Source codes are available on GitHub `https://github.com/seznam/jobslib
<https://github.com/seznam/jobslib>`_ under the `3-clause BSD license
<https://opensource.org/licenses/BSD-3-Clause>`_.
