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

    def test_formal(self, cycle=CYCLE):
        while True:
            print('Testing Formal')
            try:
                self.tester.test_formal()
                time.sleep(cycle)
            except Exception as e:
                print(e.args)

    def test_temporary(self, cycle=CYCLE):
        while True:
            print('Testing Temporary')
            try:
                time.sleep(cycle / 2)
                self.tester.test_temporary()
                time.sleep(cycle / 2)
            except Exception as e:
                print(e.args)

    def api(self):
        app.run(host=API_HOST, port=API_PORT)

    def run(self):
        if TEST_TEMPORARY_PROCESS:
            test_temporary_process = Process(target=self.test_temporary)
            test_temporary_process.start()

        if TEST_FORMAL_PROCESS:
            test_formal_process = Process(target=self.test_formal)
            test_formal_process.start()

        if GET_PROXY_PROCESS:
            get_proxy_process = Process(target=self.get_proxy)
            get_proxy_process.start()

        if API_PROCESS:
            api_process = Process(target=self.api)
            api_process.start()
