
jobslib
=======

**Jobslib** is a library for launching Python tasks in parallel environment.
Our use-case is. We have two datacenters (in near future three datacenters),
in each datacenter is run server with some task. However only one task may
be active at one time across all datacenters. **Jobslib** solves this problem.

Main features are:

- Ancestor for class which holds configuration.
- Ancestor for container for shared resources, e.g. database connection.
- Ancestor for class with task.
- Configurable either from configuration file or from environmet variables.
- Liveness – mechanism for exporting informations about health state of
  the task. Jobslib includes implementation which uses
  `Consul <https://www.consul.io/>`_.
- Metrics – mechanism for exporting metrics. Jobslib includes implementation
  which uses `InfluxDB <https://www.influxdata.com/>`_.
- One Instance Lock – lock, which allowes only one running instance at the
  same time. Jobslib includes implementation which uses
  `Consul <https://www.consul.io/>`_.

Installation
------------

Installation from source code:

::

    $ git clone https://github.com/seznam/jobslib.git
    $ cd jobslib
    $ python setup.py install

Installation from PyPi:

::

    $ pip install jobslib

`Tox <https://tox.readthedocs.io/en/latest/>`_ is used for testing:

::

    $ git clone https://github.com/seznam/jobslib.git
    $ cd jobslib
    $ pip install tox
    $ tox --skip-missing-interpreters

Usage
-----

Task is launched from command line using `runjob` command:

::

    $ runjob [-s SETTINGS] [--disable-one-instance] [--run-once]
             [--sleep-interval SLEEP_INTERVAL] [--run-interval RUN_INTERVAL]
             [--keep-lock] [--release-on-error]
             task_cls

    # Pass settings module using -s argument
    $ runjob -s myapp.settings myapp.task.HelloWorldTask --run-once

    # Pass settings module using environment variable
    $ export JOBSLIB_SETTINGS_MODULE="myapp.settings"
    $ runjob myapp.task.HelloWorldTask --run-once

If you want to write your own task, inherit `BaseTask` class and override
`BaseTask.task()` method. According to your requirements inherit and
override `Config` and/or `Context` and set **settings** module.

::

    class HelloWorldTask(BaseTask):

        name = 'helloworld'
        description = 'prints hello world'

        def task(self):
            sys.stdout.write('Hello World!\n')
            sys.stdout.flush()

License
-------

3-clause BSD

Documentation
-------------

https://seznam.github.io/jobslib/
