import redis
import random
from proxyfilter.config import *


class RedisClient(object):
    def __init__(self, host=HOST, port=PORT, domain=DOMAIN, type=TYPE):
        if PASSWORD:
            self._db = redis.Redis(host=host, port=port, password=PASSWORD)
        else:
            self._db = redis.Redis(host=host, port=port)
        self.domain = domain
        self.type = type

    def keys(self):
        return self._db.keys(self._key('*'))

    def random(self):
        random_key = random.choice(self._db.keys(self.domain + ':*'))
        try:
            type = random_key.decode('utf-8').split(':')[1]
        except IndexError:
            type = 'http'
        proxy = self._db.srandmember(random_key)
        return {
            'type': type,
            'proxy': proxy.decode('utf-8').strip()
        }

    def all(self, scheme):
        return self._db.smembers(self._key(scheme))

    def _key(self, scheme):
        return '{domain}:{type}:{scheme}'.format(domain=self.domain, type=self.type, scheme=scheme)

    def add(self, scheme, proxy):
        """
        add proxy
        :param scheme: 协议类型，如http, https
        :param proxy: 代理
        :return:
        """
        return self._db.sadd(self._key(scheme), proxy.strip())

    def remove(self, scheme, proxy):
        """
        移除
        :param scheme:
        :param proxy:
        :return:
        """
        return self._db.srem(self._key(scheme), proxy)

    def flush(self):
        """
        flush db
        """
        return self._db.flushall()



