
import os
import sys
import time

from jobslib import BaseTask

# settings --------------------------------------------------------------------

# ONE_INSTANCE_BACKEND = 'jobslib.oneinstance.dummy.DummyLock'
ONE_INSTANCE = {
    'backend': 'jobslib.oneinstance.consul.ConsulLock',
    'options': {
        'key': 'example-oneinstance',
        'ttl': 60,
    }
}

CONSUL = {
    'host': '127.0.0.1',
}


# task ------------------------------------------------------------------------

class OneInstance(BaseTask):

    name = 'oneinstance'
    description = 'task which is run only in one instance at the same time'
    arguments = ()

    def task(self):
        for i in range(10, 0, -1):
            sys.stdout.write("\r[{}] {}\x1b[K".format(os.getpid(), i))
            sys.stdout.flush()
            time.sleep(1.0)
        sys.stdout.write("\r[{}] Done\x1b[K\n".format(os.getpid()))
        sys.stdout.flush()
