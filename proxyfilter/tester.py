import json
from urllib.parse import parse_qs

from proxyfilter.db import RedisClient
from proxyfilter import grequests
from proxyfilter.config import *


class ValidTester():
    def __init__(self):
        self.conn = RedisClient()
    
    def exception(self, request, exception):
        proxies = request.kwargs.get('proxies')
        scheme = list(proxies.keys())[0]
        proxy = proxies.get(scheme).replace(scheme + '://', '')
        print('Get Exception of', scheme, proxy, 'Down it')
        self.conn.down(scheme, proxy)
    
    def valid_test(self):
        keys = self.conn.keys()
        for key in keys:
            scheme = key.decode('utf-8').split(':')[1]
            queue = []
            proxies = self.conn.all(scheme)
            for proxy in proxies:
                proxy = proxy.decode('utf-8').strip()
                queue.append(grequests.post(TEST_URL, proxies={
                    scheme: scheme + '://' + proxy
                }, data={
                    'proxy': proxy
                }))
            responses = grequests.map(queue, exception_handler=self.exception, gtimeout=5)
            for response in responses:
                if not response is None:
                    if response.status_code == 200:
                        result = json.loads(response.text)
                        origin = result.get('origin')
                        proxy = result.get('form').get('proxy')
                        if origin != proxy.split(':')[0]:
                            print('Invalid Proxy', proxy, 'Down', scheme, proxy)
                            self.conn.down(scheme, proxy)
                        else:
                            print('Valid Proxy', scheme, proxy)
                            self.conn.up(scheme, proxy)
                    else:
                        proxy = parse_qs(response.request.body).get('proxy')[0]
                        print('Status Code Not Valid, Invalid Proxy', proxy, 'Down', scheme, proxy)
                        self.conn.down(scheme, proxy)
