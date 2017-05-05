import time
from multiprocessing import Process
from proxyfilter.api import app
from proxyfilter.config import *
from proxyfilter.getter import ProxyGetter
from proxyfilter.tester import ValidTester


class Scheduler():
    def __init__(self):
        self.getter = ProxyGetter()
        self.tester = ValidTester()

    def get_proxy(self, cycle=CYCLE):
        while True:
            print('Getting Proxies')
            try:
                self.getter.run()
                time.sleep(cycle)
            except Exception as e:
                print(e.args)

    def valid_test(self, cycle=CYCLE):
        while True:
            print('Testing')
            try:
                self.tester.valid_test()
                time.sleep(cycle)
            except Exception as e:
                print(e.args)

    def api(self):
        app.run(host=API_HOST, port=API_PORT)

    def run(self):
        if VALID_TEST_PROCESS:
            valid_test_process = Process(target=self.valid_test)
            valid_test_process.start()

        if GET_PROXY_PROCESS:
            get_proxy_process = Process(target=self.get_proxy)
            get_proxy_process.start()

        if API_PROCESS:
            api_process = Process(target=self.api)
            api_process.start()
