from proxyfilter.db import RedisClient


class Importer():
    def __init__(self):
        self.conn = RedisClient()

    def add(self, proxy):
        result = self.conn.add(self.scheme, proxy)
        print('录入成功' if result else '录入失败', proxy)

    def scan(self):
        print('请输入协议:')
        self.scheme = input()
        print('请输入代理:')
        while True:
            proxy = input()
            if proxy == 'exit':
                break
            self.add(proxy)

if __name__ == '__main__':
    importer = Importer()
    importer.scan()
