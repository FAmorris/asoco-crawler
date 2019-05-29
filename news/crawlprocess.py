from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from universal.utils import get_config
from scrapy.settings import Settings


def get_crawler_process(name):
    '''
    建立爬虫进程，开始爬取
    '''
    custom_settings = get_config(name)
    '''
    获取爬虫配置信息
    '''
    spider = custom_settings.get('spider', 'universal')
    project_settings = Settings()
    project_settings.setmodule("universal.settings")
    settings = dict(project_settings.copy())
    '''
    根据爬虫配置信息中的settings属性，更新settings.py相应配置项
    '''
    settings.update(custom_settings.get('settings', {}))
    #开启爬虫进程
    process = CrawlerProcess(settings)
    process.crawl(spider, **{'name': name})
    return process
