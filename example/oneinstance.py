
import os
import sys
import time

from jobslib import BaseTask

# settings --------------------------------------------------------------------

ONE_INSTANCE = {
    'backend': 'jobslib.oneinstance.consul.ConsulLock',
    'options': {
        'key': 'jobs/example/oneinstance/lock',
        'ttl': 30,
        'lock_delay': 5,
    }
}

LIVENESS = {
    'backend': 'jobslib.liveness.consul.ConsulLiveness',
    'options': {
        'key': 'jobs/example/oneinstance/liveness',
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
            if self.context.one_instance_lock.refresh():
                sys.stdout.write("\r[{}] {}\x1b[K".format(os.getpid(), i))
                sys.stdout.flush()
                time.sleep(5.0)
        sys.stdout.write("\r\x1b[K")
        sys.stdout.flush()
