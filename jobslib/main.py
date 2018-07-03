"""
Modul :module:`jobslib.main` is an entry point from command line into
**jobslib** tasks.
"""

import importlib
import itertools
import os

from .cmdlineparser import ArgumentParser
from .config import Config
from .exceptions import ImproperlyConfiguredError
from .imports import import_object
from .tasks import BaseTask


__all__ = ['main']


def get_app_settings(cmdline_args):
    """
    Return **settings** module of the application according to either
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
        help='task settings module'
    )
    parser.add_argument(
        'task_cls', action='store', type=str,
        help='module path to task class (module.submodule.TaskClass)'
    )
    cmdline_args, unused_remaining = parser.parse_known_args(args)

    # Obtain settings module
    try:
        settings = get_app_settings(cmdline_args)
    except ImportError as exc:
        parser.error("Invalid application settings module: {}".format(exc))
    # Obtain task class and add its arguments into parser
    try:
        task_cls = get_task_cls(cmdline_args.task_cls)
    except (ImportError, AttributeError) as exc:
        parser.error(exc)

    # Enrich parser with task arguments
    for task_args, task_kwargs in task_cls.arguments:
        parser.add_argument(*task_args, **task_kwargs)

    # Obtain config class and enrich parser with config arguments
    config_cls = get_config_class(settings)
    if not issubclass(config_cls, Config):
        parser.error(
            "Config class must be subclass of the jobslib.config.Config")
    for config_args, kwargs in itertools.chain(
            config_cls._base_arguments, config_cls.arguments):
        parser.add_argument(*config_args, **kwargs)

    # Add help argument
    parser.add_argument(
        '-h', '--help', action='help',
        help='show this help message and exit'
    )
    # Parse command line
    cmdline_args = parser.parse_args(args)

    # Launch task
    try:
        config = config_cls(settings, cmdline_args)
    except ImproperlyConfiguredError as exc:
        parser.error(str(exc))
    task = task_cls(config)
    task()


if __name__ == '__main__':
    main()
