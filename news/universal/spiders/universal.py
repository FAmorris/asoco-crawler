# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from universal.items import *
from universal.utils import *
from universal.extractors import RegexLinkExtractor
from scrapy import Request
from universal import urls
from scrapy_splash import SplashRequest
import re

class UniversalSpider(CrawlSpider):
    name = 'universal'

    def __init__(self, name, *args, **kwargs):
        '''
        获取配置文件中的信息
        '''
        config = get_config(name)
        self.config = config
        self.rules = eval(config.get('rules'))
        #self.start_urls = config.get('start_urls')
        #'''
        start_urls = config.get('start_urls')
        self.index = config.get('index')
        print(start_urls)
        if start_urls:
            if start_urls.get('type')=='static':
                self.start_urls=start_urls.get('values')
            elif start_urls.get('type')=='dynamic':
                self.start_urls = list(eval('urls.' + start_urls.get('method'))(*start_urls.get('args', [])))
            if start_urls.get('splash'):
                splash = start_urls.get('splash')
                if splash.get('enable'):
                    self.start_urls_splash_enable = True
                    if splash.get('args'):
                        self.start_urls_splash_args = splash.get('args')
                else:
                    self.start_urls_splash_enable = False
        if config.get('splash'):
            splash = config.get('splash')
            auth = splash.get('auth')
            self.http_user = auth.get('user')
            self.http_pass = auth.get('password')
        #'''
        self.allowed_domains = config.get('allowed_domains')
        super(UniversalSpider, self).__init__(*args, **kwargs)

    def start_requests(self):
        '''
        判断是否使用splash，返回request或splashrequest
        :return: 
        '''
        for url in self.start_urls:
            request = Request(url, dont_filter=True)
            yield self.splash_request(request,
                                      args=self.start_urls_splash_args) if self.start_urls_splash_enable else request

    def splash_request(self, request, args={'wait': 1}):
        '''
        如果使用splash,需要将request转换为splashrequest
        :param request: 
        :param args: 
        :return: 
        '''
        meta = request.meta
        url=request.url
        index = self.index
        url=re.sub(self.settings['SPLASH_URL'],index,url)
        meta.update({'url': url})
        return SplashRequest(url=url, dont_process_response=True, args=args,
                             callback=request.callback,
                             meta=meta)

    def splash_request_video(self, request, args={'wait': 1}):
        '''
        如果使用splash,需要将request转换为splashrequest
        :param request:
        :param args:
        :return:
        '''
        index = self.index
        url = index + request.url.replace(self.settings['SPLASH_URL'],'')
        meta = request.meta
        meta.update({'url': url})
        return SplashRequest(url=url, dont_process_response=True, args=args,
                             callback=request.callback,
                             meta=meta)

    def splash_request_video_mod_gov(self, request, args={'wait': 1}):
        '''
        如果使用splash,需要将request转换为splashrequest
        :param request:
        :param args:
        :return:
        '''
        index = self.index
        result = re.search("http://www.mod.gov.cn/v/",index)
        url = result.group(0) +request.url.replace(self.settings['SPLASH_URL'],'')
        meta = request.meta
        meta.update({'url': url})
        return SplashRequest(url=url, dont_process_response=True, args=args,
                             callback=request.callback,
                             meta=meta)

    def parse_item(self, response):
        # 获取item配置
        if response.meta.get('url'):
            response = response.replace(url=response.meta.get('url'))
        item = self.config.get('item')
        if item:
            data = eval(item.get('class') + '()')
            # 动态获取属性配置
            for key, value in item.get('attrs').items():
                data[key] = response
                for process in value:
                    type = process.get('type', 'chain')
                    if type == 'chain':
                        # 动态调用函数和属性
                        if process.get('method'):
                            data[key] = getattr(data[key], process.get('method'))(*process.get('args', []))
                    elif type == 'wrap':
                        args = [data[key]] + process.get('args', [])
                        data[key] = (eval(process.get('method'))(*args))
            yield data

    # 添加_build_request函数，避免版本问题
    def _build_request(self, rule, link):
        r = Request(url=link.url, callback=self._response_downloaded)
        r.meta.update(rule=rule, link_text=link.text)
        return r

    def _requests_to_follow(self, response):
        seen = set()
        for n, rule in enumerate(self._rules):
            links = [lnk for lnk in rule.link_extractor.extract_links(response)
                     if lnk not in seen]
            if links and rule.process_links:
                links = rule.process_links(links)
            for link in links:
                seen.add(link)
                r = self._build_request(n, link)
                yield rule.process_request(r)
