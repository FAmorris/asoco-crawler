from scrapy.link import Link
from scrapy.utils.python import unique as unique_list, to_native_str
from scrapy.utils.response import get_base_url
import re


class RegexLinkExtractor():
    '''
    获取rule中的xpath,css区域，提取出他的url做下一步跟进
    '''
    def __init__(self, restrict_re='', base_url=None):
        self.restrict_re = restrict_re
        self.base_url = base_url
    
    def extract_links(self, response):
        if not self.base_url:
            self.base_url = get_base_url(response)
        items = re.findall(self.restrict_re, response.text)
        all_links = [Link(response.urljoin(self.base_url.format(str(item)))) for item in items]
        return unique_list(all_links)


import json
from scrapy.utils.python import unique as unique_list
from scrapy.link import Link
from scrapy.spiders import CrawlSpider as BaseSpider, signals


class JsonLinkExtractor():
    '''
    解析返回的json数据
    '''
    def __init__(self, patterns):
        self.patterns = patterns
    
    def get_value(self, dict, *keys):
        if len(keys) == 1:
            return dict.get(keys[0])
        else:
            result = []
            for key in keys:
                result.append(dict.get(key))
        return result
    
    def get_slice(self, list, start, end=None):
        if start == '*':
            return list
        else:
            return list[start:end]
    
    def extract_links(self, response):
        result = json.loads(response.text)
        for pattern in self.patterns:
            extractors = pattern.get('extractors')
            format = pattern.get('format')
            data = result
            for extractor in extractors:
                type = extractor.get('type')
                if isinstance(data, dict):
                    if type == 'value':
                        data = self.get_value(*([data] + extractor.get('args')))
                elif isinstance(data, list):
                    if type == 'value':
                        data = [self.get_value(*([item] + extractor.get('args'))) for item in data]
                    elif type == 'slice':
                        data = self.get_slice(*([data] + extractor.get('args')))
            if not isinstance(data, list):
                data = [data]
            all_links = [Link(response.urljoin(format.format(*[item]))) if not isinstance(item, list) else
                         Link(response.urljoin(format.format(*item))) for item in data]
            return unique_list(all_links)
