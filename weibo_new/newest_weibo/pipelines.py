# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymongo, re, time, datetime

from weibo_new.newest_weibo.items import UserItem, WeiboItem

from py2neo.ogm import GraphObject, Property, RelatedTo, RelatedFrom, Related

from py2neo import Graph, Node, Relationship

from weibo_new.newest_weibo.settings import NEO4J_URL


class TimePipeline():
    """
    时间修改，添加爬取时间一项
    """
    
    def process_item(self, item, spider):
        if isinstance(item, UserItem) or isinstance(item, WeiboItem):
            now = time.strftime('%Y-%m-%d %H:%M', time.localtime())
            item['crawled_at'] = now
        return item


class WeiboPipeline():
    """
    处理微博日期，对于刚刚，几分钟前这样的时间表示，使用正则匹配，转化为形如%Y-%m-%d %H:%M的时间格式
    """
    
    def parse_time(self, date):
        if re.match('刚刚', date):
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
            return date
        if re.match('\d+分钟前', date):
            minute = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(minute) * 60))
            return date
        if re.match('\d+小时前', date):
            hour = re.match('(\d+)', date).group(1)
            date = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time() - float(hour) * 60 * 60))
            return date
        if re.match('昨天.*', date):
            date = re.match('昨天(.*)', date).group(1).strip()
            date = time.strftime('%Y-%m-%d', time.localtime(time.time() - 24 * 60 * 60)) + ' ' + date
            return date
        if re.match('\d{2}-\d{2}', date):
            date = time.strftime('%Y-', time.localtime()) + date + ' 00:00'
            return date
        else:
            FORMAT = '%a %b %d %H:%M:%S +0800 %Y'
            date1 = time.strptime(date, FORMAT)
            date = time.strftime('%Y-%m-%d %H:%M', date1)
            return date
    """
    将处理后的date，存入created_at项中
    """
    def process_item(self, item, spider):
        if isinstance(item, WeiboItem):
            if item.get('created_at'):
                item['created_at'] = item['created_at'].strip()
                item['created_at'] = self.parse_time(item.get('created_at'))
                # if item.get('pictures'):
                #     item['pictures'] = [pic.get('url') for pic in item.get('pictures')]
        return item


class MongoPipeline(object):
    """
    存储到MongoDB中
    """
    
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_url = mongo_uri
        self.mongo_db = mongo_db
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DB')
        )

    """
    建立MongoDB连接和用户节点，微博节点的索引
    """
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_url)
        self.db = self.client[self.mongo_db]
        self.db.userInfo.create_index([('id', pymongo.ASCENDING)])
        self.db.weiboInfo.create_index([('id', pymongo.ASCENDING)])
    
    """
    判断item是用户类型还是微博类型，将其写入MongoDB中
    """
    def process_item(self, item, spider):
        if isinstance(item, UserItem):
            self.db.userInfo.update({'id': item.get('id')}, {'$set': item}, True)
        if isinstance(item, WeiboItem):
            self.db.weiboInfo.update({'id': item.get('id')}, {'$set': item}, True)
        return item
    
    def close_spider(self, spider):
        self.client.close()


class User(GraphObject):
    """
    存Neo4j的Gragh对象
    """
    __primarykey__ = 'id'
    
    id = Property()
    image = Property()
    name = Property()
    cover = Property()
    description = Property()
    follows_count = Property()
    fans_count = Property()
    gender = Property()
    statuses_count = Property()
    verified = Property()
    verified_reason = Property()
    verified_type = Property()
    flag = Property()
    publish = Related('Weibo', 'PUBLISH')


class Weibo(GraphObject):
    """
    存Neo4j的Gragh对象
    """
    __primarykey__ = 'id'
    
    id = Property()
    attitudes_count = Property()
    comments_count = Property()
    reposts_count = Property()
    text = Property()
    raw_text = Property()
    text_length = Property()
    thumbnail_picture = Property()
    pictures = Property()
    user = Property()
    source = Property()
    is_long_text = Property()
    created_at = Property()
    origin = Property()
    pid = Property()
    keyword = Property()
    
    repost = RelatedTo('Weibo', 'REPOST')
    publish = Related('User', 'PUBLISH')


class NeoPipeline(object):
    """
    Neo4j存储
    """
    # graph = Graph(password = '1234')#默认为本地连接
    graph = Graph(
        NEO4J_URL['url'],
        username=NEO4J_URL['username'],
        password=NEO4J_URL['password']
    )
    
    def process_item(self, item, spider):
        if isinstance(item, WeiboItem):
            """
            item属于微博类型时
            """
            weibo = Weibo()
            
            weibo.id = item['id']
            weibo.attitudes_count = item['attitudes_count']
            weibo.comments_count = item['comments_count']
            weibo.reposts_count = item['reposts_count']
            weibo.text = item['text']
            weibo.raw_text = item['raw_text']
            weibo.text_length = item['text_length']
            weibo.thumbnail_picture = item['thumbnail_picture']
            weibo.pictures = item['pictures']
            weibo.user = item['user']
            weibo.source = item['source']
            weibo.is_long_text = item['is_long_text']
            weibo.created_at = item['created_at']
            weibo.origin = item['origin']
            weibo.pid = item['pid']
            weibo.keyword = item['keyword']
            
            # self.graph.create(weibo)#插入微博节点
            """
            根据爬取到微博信息中的用户信息，查找数据库中对应的用户节点，建立用户与微博的发布关系
            """
            user = User.select(self.graph).where(id=item['user']).first()
            print('user------------------\n', user)
            user.publish.add(weibo)  # 通过发布关系插入微博节点（做到同时插入微博节点和相应的发布无向边）,如果不存在则添加，存在则更新
            self.graph.push(user)  # 更新数据库
            # self.graph.push(weibo)
            """
            建立微博节点与微博节点之间的转发关系
            """
            # if item['pid'] == str(0) and Weibo.select(self.graph).where(id=item['id']).first() == None:  # 表示根微博（？是否需要查找存在与否）
            if item['pid'] == 0:  # 表示根微博（？是否需要查找存在与否）
                pass
            # elif item['pid']=='' and Weibo.select(self.graph).where(id=item['id']).first() == None:  # 最内层直接转发的微博
            elif item['pid'] == None:  # 最内层直接转发的微博
                # 方案二：
                # root_weibo = Weibo.select(self.graph).where(id=item['origin']).first()#获取根微博
                # repost_relationship =Relationship(dict(weibo),'REPOST',dict(root_weibo))#转发关系
                # self.graph.create(repost_relationship)#插入转发关系边到数据库
                
                # 方案一
                # print('666666666666666666666666666666666\n\n\n')
                # print('-------------------origin\n\n',item['origin'],type(item['origin']))
                
                root_weibo = Weibo.select(self.graph).where(id=str(item['origin'])).first()  # 获取根微博
                
                print('-------------------root_weibo\n\n', root_weibo)
                weibo = Weibo.select(self.graph).where(id=item['id']).first()  # 获取刚刚插入的最内层微博
                weibo.repost.add(root_weibo)  # 建立和根微博的关系（有向边）
                self.graph.push(weibo)
            # elif item['pid']!=str(0) and item['pid']!='' and Weibo.select(self.graph).where(id=item['id']).first() == None: #最外层以及中间层微博
            elif item['pid'] != 0 and item['pid'] != None:  # 最外层以及中间层微博
                
                # 方案一
                print('77777777777777777777777\n\n\n')
                
                next_weibo = Weibo()  # 预先插入下一层转发微博id
                next_weibo.id = str(item['pid'])  # 下一层id=本层pid
                weibo = Weibo.select(self.graph).where(id=item['id']).first()  # 获取刚刚插入的最外层微博
                weibo.repost.add(next_weibo)  # 建立和转发下一层微博的关系（有向边），并预插入id
                self.graph.push(weibo)  # ？和之前插入微博节点重复，更新两次，可优化
                
                # 优化方案二如下：不利用ogm
                # next_weibo = Weibo()  # 预先插入下一层转发微博id
                # next_weibo.id = item['pid']  # 下一层id=本层pid
                # weibo = Weibo.select(self.graph).where(id=item['id']).first()  # 获取刚刚插入的最外层微博
                # w= dict(weibo)
                # ww=dict(next_weibo)
                # repost_relationship = Relationship(w, 'REPOST',ww )  # 转发关系
                # self.graph.create(next_weibo)
                # self.graph.create(repost_relationship)
                # elif item['pid']!=str(0) and item['pid']!='' and Weibo.select(self.graph).where(id=item['id']).first() != None: #中间层微博
        
        if isinstance(item, UserItem):
            """
            如果是用户节点，直接写入数据库
            """
            user = User()
            
            user.id = item['id']
            user.image = item['image']
            user.name = item['name']
            user.cover = item['cover']
            user.description = item['description']
            user.follows_count = item['follows_count']
            user.fans_count = item['fans_count']
            user.gender = item['gender']
            user.statuses_count = item['statuses_count']
            user.verified = item['verified']
            user.verified_reason = item['verified_reason']
            user.verified_type = item['verified_type']
            user.flag = item['flag']
            
            self.graph.push(user)  # 插入用户信息节点
