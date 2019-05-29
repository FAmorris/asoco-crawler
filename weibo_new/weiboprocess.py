from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from weibo_new.newest_weibo.spiders.weibo import WeiboSpider
from newest_weibo import settings as weibo_settings
import os
def get_crawler_process():
    """
    爬虫运行入口
    :return:
    """
    project_settings = Settings()
    print(os.path.abspath(__file__))
    project_settings.setmodule(weibo_settings)
    settings = dict(project_settings.copy())
    print(settings)
    process = CrawlerProcess(settings)
    process.crawl(WeiboSpider)
    return process


if __name__ == '__main__':
    process = get_crawler_process()
    process.start()
