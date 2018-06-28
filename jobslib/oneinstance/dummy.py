
from . import BaseLock


class DummyLock(BaseLock):

    def acquire(self):
        return True

    def release(self):
        return True

    def refresh(self):
        return True
