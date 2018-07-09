"""
JobsLib exceptions.
"""

__all__ = ['JobsLibError', 'TaskError']


class JobsLibError(Exception):
    """
    Base error, ancestor for all other JobsLib errors.
    """

    pass


class TaskError(JobsLibError):
    """
    Task error.
    """

    pass
