import json
from urllib.parse import parse_qs

from proxyfilter.db import RedisClient
import grequests
from proxyfilter.config import *


class ValidTester():
    def __init__(self):
        self.conn_formal = RedisClient(type='formal')
        self.conn_temporary = RedisClient(type='temporary')
    
    def exception(self, request, exception):
        print('Get Exception', request, exception)

    def test_temporary(self):
        keys = self.conn_temporary.keys()
        for key in keys:
            scheme = key.decode('utf-8').split(':')[2]
            queue = []
            proxies = self.conn_temporary.all(scheme)
            for proxy in proxies:
                proxy = proxy.decode('utf-8').strip()
                queue.append(grequests.post(TEST_URL, proxies={
                    scheme: scheme + '://' + proxy
                }, data={
                    'proxy': proxy
                }))
            responses = grequests.map(queue, exception_handler=self.exception, gtimeout=5)
            print(responses)
            for response in responses:
                print(response)
                if not response is None:
                    if response.status_code == 200:
                        result = json.loads(response.text)
                        origin = result.get('origin')
                        proxy = result.get('form').get('proxy')
                        if origin != proxy.split(':')[0]:
                            print('Temporary Tester: Invalid Proxy', proxy, 'Delete', scheme, proxy)
                            self.conn_temporary.remove(scheme, proxy)
                        else:
                            print('Temporary Tester: Valid Proxy', scheme, proxy, 'Add it to Formal Pool')
                            self.conn_formal.add(scheme, proxy)
                    else:
                        proxy = parse_qs(response.request.body).get('proxy')[0]
                        print('Temporary Tester: Status Code Not Valid, Invalid Proxy', proxy, 'Delete', scheme, proxy)
                        self.conn_temporary.remove(scheme, proxy)
                else:
                    print('None', response)
    
    def test_formal(self):
        keys = self.conn_formal.keys()
        print(keys)
        for key in keys:
            scheme = key.decode('utf-8').split(':')[2]
            queue = []
            proxies = self.conn_formal.all(scheme)
            for proxy in proxies:
                proxy = proxy.decode('utf-8').strip()
                queue.append(grequests.post(TEST_URL, proxies={
                    scheme: scheme + '://' + proxy
                }, data={
                    'proxy': proxy
                }))
            responses = grequests.map(queue, exception_handler=self.exception, gtimeout=5)
            print(responses)
            for response in responses:
                print(response)
                if not response is None:
                    if response.status_code == 200:
                        result = json.loads(response.text)
                        origin = result.get('origin')
                        proxy = result.get('form').get('proxy')
                        if origin != proxy.split(':')[0]:
                            print('Formal Tester: Invalid Proxy', proxy, 'Delete', scheme, proxy)
                            self.conn_formal.remove(scheme, proxy)
                        else:
                            print('Formal Tester: Valid Proxy', scheme, proxy)
                    else:
                        proxy = parse_qs(response.request.body).get('proxy')[0]
                        print('Formal Tester: Status Code Not Valid, Invalid Proxy', proxy, 'Delete', scheme, proxy)
                        self.conn_formal.remove(scheme, proxy)
                else:
                    print('None', response)


if __name__ == '__main__':
    tester = ValidTester()
    tester.run()
