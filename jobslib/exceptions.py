"""
JobsLib exceptions.
"""

__all__ = ['JobsLibError', 'ImproperlyConfiguredError', 'TaskError']


class JobsLibError(Exception):
    """
    Base error, ancestor for all other JobsLib errors.
    """

    pass


class ImproperlyConfiguredError(JobsLibError):
    """
    Configuration error.
    """

    pass


class TaskError(JobsLibError):
    """
    Task error.
    """

    pass
