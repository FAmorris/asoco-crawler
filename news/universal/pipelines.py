# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import re

class UniversalPipeline(object):
    """
    关键词过滤
    """
    def process_item(self, item, spider):
        keywords = [
            '洪水', '台风', '内涝', '暴雨', '地震', '泥石流', '山体滑坡', '龙卷风', '自然', '灾害',
            '火灾', '重大车辆事故', '拆迁', '上访', '维权', '化学事故', '化工厂', '核事故', '核电厂', '重大集会', '演唱会', '党委', '政府', '人大', '政协', '倒塌',
            '油库', '油车', '加油站', '煤气', '毒气', '杀人', '东伊运', '暴恐', '恐怖', '“伊吉拉特”', '公共', '卫生', '事件', '社会', '安全', '事件'
                                                                                                            '军人', '假军人',
            '退伍军人', '退役士兵', '退役军人', '军车', '飞机', '舰艇', '省军区', '军分区', '人武部', '专武干部', '专武部长'
        ]
        for keyword in keywords:
            if keyword in item['title'] or keyword in item['content']:
                return item
        return item

class MySQLPipelineUnique():
    '''
    写入mysql，包含去重
    '''
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT'),
        )
    
    def open_spider(self, spider):
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8',
                                  port=self.port)
        self.cursor = self.db.cursor()
    
    def close_spider(self, spider):
        self.db.close()
    
    def process_item(self, item, spider):
        data = dict(item)

        if not item['publish_time']:
            item['publish_time'] = item['crawl_time']
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql='INSERT IGNORE INTO {table}({keys}) VALUES ({values})'.format(table=item.table, keys=keys,
                                                                                             values=values)
        self.cursor.execute(sql, tuple(data.values()))
        self.db.commit()
        return item


class MySQLPipeline():
    '''
    写入mysql
    '''
    def __init__(self, host, database, user, password, port):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('MYSQL_HOST'),
            database=crawler.settings.get('MYSQL_DATABASE'),
            user=crawler.settings.get('MYSQL_USER'),
            password=crawler.settings.get('MYSQL_PASSWORD'),
            port=crawler.settings.get('MYSQL_PORT'),
        )

    def open_spider(self, spider):
        self.db = pymysql.connect(self.host, self.user, self.password, self.database, charset='utf8',
                                  port=self.port)
        self.cursor = self.db.cursor()

    def close_spider(self, spider):
        self.db.close()

    def process_item(self, item, spider):
        data = dict(item)
        if not item['publish_time']:
            item['publish_time'] = item['crawl_time']
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = 'insert into %s (%s) values (%s)' % (item.table, keys, values)
        self.cursor.execute(sql, tuple(data.values()))
        self.db.commit()
        return item