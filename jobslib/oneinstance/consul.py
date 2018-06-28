
import socket

import ujson

from . import BaseLock
from ..config import ConfigGroup
from ..objectvalidator import option
from ..time import get_current_time, to_local, to_utc


class ConsulLock(BaseLock):

    class OptionsConfig(ConfigGroup):

        @option(required=True, attrtype=str)
        def key(self):
            """
            Key under which the lock is stored.
            """
            return self._settings['key']

        @option(attrtype=int)
        def ttl(self):
            """
            Maximum lock lifespan in seconds.
            """
            one_day_seconds = 60 * 60 * 24
            ttl = self._settings.get('ttl', one_day_seconds)
            if ttl < 10 or ttl > one_day_seconds:
                raise ValueError(
                    'TTL must be between 10 and {} seconds'.format(
                        one_day_seconds))
            return ttl

    def __init__(self, context, options):
        super().__init__(context, options)
        self.session_id = None

    def acquire(self):
        consul = self.context.consul

        timestamp = get_current_time()
        record = {
            'fqdn': socket.getfqdn(),
            'timestamp': timestamp,
            'time_utc': to_utc(timestamp),
            'time_local': to_local(timestamp),
        }

        self.session_id = consul.session.create(ttl=self.options.ttl)
        return consul.kv.put(
            self.options.key, ujson.dumps(record), acquire=self.session_id)

    def release(self):
        res = self.context.consul.kv.put(
            self.options.key, '{}', release=self.session_id)
        self.session_id = None
        return res

    def refresh(self):
        if self.acquire():
            session_id = self.context.consul.session.renew(
                self.context.consul_session_id)
            return session_id == self.context.consul_session_id
        return False
