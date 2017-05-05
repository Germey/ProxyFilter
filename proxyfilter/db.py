import redis
import random
from proxyfilter.config import *


class RedisClient(object):
    def __init__(self, host=HOST, port=PORT, domain=DOMAIN):
        if PASSWORD:
            self._db = redis.Redis(host=host, port=port, password=PASSWORD)
        else:
            self._db = redis.Redis(host=host, port=port)
        self.domain = domain

    def keys(self):
        return self._db.keys(self._key('*'))

    def random(self):
        random_key = random.choice(self._db.keys(self.domain + ':*'))
        try:
            scheme = random_key.decode('utf-8').split(':')[1]
        except IndexError:
            scheme = 'http'
        try:
            top_value = self._db.zrevrange(self._key(scheme), 0, 1)[0].decode('utf-8')
        except:
            return None
        top = self._db.zscore(self._key(scheme), top_value)
        half = top / 2
        results = self._db.zrevrangebyscore(self._key(scheme), max=top, min=half)
        proxy = random.choice(results)
        return {
            'scheme': scheme,
            'proxy': proxy.decode('utf-8').strip()
        }

    def all(self, scheme):
        return self._db.zrange(self._key(scheme), 0, -1)

    def _key(self, scheme):
        """
        Get Key
        :param scheme:
        :return:
        """
        return '{domain}:{scheme}'.format(domain=self.domain, scheme=scheme)

    def up(self, scheme, proxy):
        """
        Up Score, If More Than MAX_SCORE, Stay It
        :param scheme:
        :param proxy:
        :return:
        """
        score = self._db.zscore(self._key(scheme), proxy)
        self._db.zincrby(self._key(scheme), proxy, 0 if score >= MAX_SCORE else 1)

    def down(self, scheme, proxy):
        """
        Down Score, If Less Than MIN_SCORE, Delete It
        :param scheme:
        :param proxy:
        :return:
        """
        self._db.zincrby(self._key(scheme), proxy, -1)
        if self._db.zscore(self._key(scheme), proxy) <= MIN_SCORE:
            self._db.zrem(self._key(scheme), proxy)

    def add(self, scheme, proxy):
        """
        Add Proxy, Default Score 10
        :param scheme:
        :param proxy:
        :return:
        """
        return self._db.zadd(self._key(scheme), proxy, DEFAULT_SCORE)

    def remove(self, scheme, proxy):
        """
        Remove Proxy
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


if __name__ == '__main__':
    client = RedisClient()
    result = client.random()
    print(result)
