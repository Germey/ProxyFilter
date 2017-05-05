import requests
from pyquery import PyQuery as pq

from proxyfilter.db import RedisClient


class ProxyMetaclass(type):
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs['__CrawlFunc__'] = []
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append(k)
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(cls, name, bases, attrs)


class ProxyGetter(object, metaclass=ProxyMetaclass):
    def __init__(self):
        self.base_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8'
        }
        self.conn = RedisClient(type='temporary')

    def get_page(self, url, options={}):
        headers = dict(self.base_headers, **options)
        try:
            r = requests.get(url, headers=headers)
            print('Getting result', url, r.status_code)
            if r.status_code == 200:
                return r.text
        except ConnectionError:
            print('Crawling Failed', url)

    def crawl_daili66(self, page_count=10):
        start_url = 'http://www.66ip.cn/{}.html'
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        for url in urls:
            print('Crawling', url)
            html = self.get_page(url)
            if html:
                doc = pq(html)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find('td:nth-child(1)').text()
                    port = tr.find('td:nth-child(2)').text()
                    yield {
                        'scheme': 'http',
                        'proxy': ':'.join([ip, port])
                    }

    def crawl_proxy360(self):
        start_url = 'http://www.proxy360.cn/Region/China'
        print('Crawling', start_url)
        html = self.get_page(start_url)
        if html:
            doc = pq(html)
            lines = doc('div[name="list_proxy_ip"]').items()
            for line in lines:
                ip = line.find('.tbBottomLine:nth-child(1)').text()
                port = line.find('.tbBottomLine:nth-child(2)').text()
                yield {
                    'scheme': 'http',
                    'proxy': ':'.join([ip, port])
                }

    def crawl_goubanjia(self, page_count=10):
        start_url = 'http://www.goubanjia.com/free/gngn/index{}.shtml'
        urls = [start_url.format(page) for page in range(1, page_count + 1)]
        for url in urls:
            html = self.get_page(url)
            if html:
                doc = pq(html)
                trs = doc('table.table tr')
                for tr in trs.items():
                    td = tr.find('td.ip')
                    td.find('p').remove()
                    proxy = td.text().replace(' ', '')
                    scheme = tr.find('td:nth-child(3)').text()
                    if ',' in scheme:
                        scheme = scheme.split(',')[0]
                    if scheme and proxy:
                        yield {
                            'scheme': scheme,
                            'proxy': proxy
                        }

    def run(self):
        functions = self.__CrawlFunc__
        for function in functions:
            results = eval('self.' + function + '()')
            for result in results:
                print('Getting Proxy', result)
                self.conn.add(result.get('scheme'), result.get('proxy'))


