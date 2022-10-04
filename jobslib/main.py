"""
Modul :module:`jobslib.main` is an entry point from command line into
**jobslib** tasks.
"""

import importlib
import os

from .cmdlineparser import ArgumentParser
from .config import Config
from .imports import import_object
from .tasks import BaseTask


__all__ = ['main']

JOBSLIB_TASKS = {
    'check-liveness': 'jobslib.liveness.CheckLiveness',
}


def get_app_settings(cmdline_args):
    """
    Return :mod:`settings` module of the application according to either
    command line argument **-s/--settings** or **JOBSLIB_SETTINGS_MODULE**
    environment variable.
    """
    settings_module_path = (
        cmdline_args.settings or os.environ.get('JOBSLIB_SETTINGS_MODULE', ''))
    if not settings_module_path:
        return None
    return importlib.import_module(settings_module_path)


def get_task_cls(task_cls_path):
    """
    Obtain from command line Python module path of the task class and
    import it.
    """
    task_cls = import_object(task_cls_path)
    if not issubclass(task_cls, BaseTask):
        raise TypeError(
            "'{}' is not subclass of the BaseTask".format(task_cls_path))
    return task_cls


def get_config_class(settings):
    """
    According to **settings.CONFIG_CLASS** return either config class
    defined by user or default :class:`shelter.core.config.Config`.
    """
    config_cls_name = getattr(settings, 'CONFIG_CLASS', '')
    if config_cls_name:
        config_cls = import_object(config_cls_name)
    else:
        config_cls = Config
    return config_cls


def main(args=None):
    """
    Parse command line and run task.
    """
    # Command line parser. Help is not allowed because command line is
    # parsed in two stages - during first stage are being parsed settings
    # module and task class, during second stage are being parsed
    # arguments of the task.
    parser = ArgumentParser(add_help=False)
    parser.add_argument(
        '-s', '--settings', action='store', dest='settings',
        type=str, default=None,
        help='task settings module')
    parser.add_argument(
        '--disable-one-instance', action='store_true',
        dest='disable_one_instance', default=False,
        help='multilple instance can be run at the same time')
    parser.add_argument(
        '--run-once', action='store_true',
        dest='run_once', default=None,
        help='run task only once and exit')
    parser.add_argument(
        '--sleep-interval', action='store', dest='sleep_interval',
        type=int, default=None,
        help='sleep interval seconds after task is done, may not be '
             'used together with --run-interval')
    parser.add_argument(
        '--run-interval', action='store', dest='run_interval',
        type=int, default=None,
        help='run task every interval seconds, may not be used together '
             'with --sleep-interval')
    parser.add_argument(
        '--keep-lock', action='store_true',
        dest='keep_lock', default=None,
        help='keep lock during sleeping interval')
    parser.add_argument(
        '--release-on-error', action='store_true',
        dest='release_on_error', default=None,
        help='release lock on task error')
    parser.add_argument(
        'task_cls', action='store', type=str,
        help='module path to task class (module.submodule.TaskClass), '
             'or some of the internal tasks ({})'.format(
                 '|'.join(JOBSLIB_TASKS.keys())))
    cmdline_args, unused_remaining = parser.parse_known_args(args)

    # Obtain settings module
    try:
        settings = get_app_settings(cmdline_args)
    except ImportError as exc:
        parser.error("Invalid application settings module: {}".format(exc))
    # Obtain task class
    if cmdline_args.task_cls in JOBSLIB_TASKS:
        task_cls = get_task_cls(JOBSLIB_TASKS[cmdline_args.task_cls])
    else:
        try:
            task_cls = get_task_cls(cmdline_args.task_cls)
        except (ImportError, AttributeError) as exc:
            parser.error(exc)

    # Enrich parser with task arguments and help
    if task_cls.description:
        parser.description = '{:s}: {:s}'.format(
            cmdline_args.task_cls, task_cls.description)
    for task_args, task_kwargs in task_cls.arguments:
        parser.add_argument(*task_args, **task_kwargs)

    # Obtain config class
    config_cls = get_config_class(settings)
    if not issubclass(config_cls, Config):
        parser.error(
            "Config class must be subclass of the jobslib.config.Config")

    # Add help argument
    parser.add_argument(
        '-h', '--help', action='help',
        help='show this help message and exit'
    )
    # Parse command line
    cmdline_args = parser.parse_args(args)
    if (cmdline_args.sleep_interval is not None and
            cmdline_args.run_interval is not None):
        parser.error(
            "--sleep-interval and --run-interval may not be used together")

    # Launch task
    config = config_cls(settings, cmdline_args, task_cls)
    task = task_cls(config)
    task()


if __name__ == '__main__':
    main()
