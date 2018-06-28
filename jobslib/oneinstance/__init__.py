
import abc

from ..config import ConfigGroup


class BaseLock(abc.ABC):

    class OptionsConfig(ConfigGroup):
        pass

    def __init__(self, context, options):
        self.context = context
        self.options = options

    @abc.abstractmethod
    def acquire(self):
        raise NotImplementedError

    @abc.abstractmethod
    def release(self):
        raise NotImplementedError

    @abc.abstractmethod
    def refresh(self):
        raise NotImplementedError
