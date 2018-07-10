# jobslib

Library for launching tasks in parallel environment. Task is launched from
command line using `runjob` command:

    runjob [-s SETTINGS] [--one-instance] [--run-once]
           [--sleep-interval SLEEP_INTERVAL] task_cls

    runjob -s myapp.settings --run-once myapp.task.HelloWorld

    export JOBSLIB_SETTINGS_MODULE="myapp.settings"
    runjob --run-once myapp.task.HelloWorld

Task is normally run in infinite loop, delay in seconds between individual
launches is controlled by `--sleep-interval` argument. If you don’t want to
launch task forever, use `--run-once` argument. If you want to launch task
on several machines and may be launched only one instance at one time,
library provides locking mechanism. In this case use `--one-instance`
argument. Optional argument `-s`/`--settings` defines Python’s module where
configuration is stored. Or you can pass settings module using
`JOBSLIB_SETTINGS_MODULE`.

During task initialization instances of the `Config` and `Context` classes
are created. You can define your own classes in the **settings** module.
`Config` is container which holds configuration. `Context` is container
which holds resources which are necessary for your task, for example
database connection. Finally, when both classes are successfuly initialized,
instance of the task (subclass of the `BaseTask` passed as `task_cls`
argument) is created and launched.

If you want to write your own task, inherit `BaseTask` class and override
`BaseTask.task()` method. According to your requirements inherit and
override `Config` and/or `Context` and set **settings** module.
