# -*- coding: utf-8 -*-
import json

import scrapy
import re
import urllib.parse

from weibo_new.newest_weibo.items import UserItem

from weibo_new.newest_weibo.items import WeiboItem

from py2neo import Graph,Node,Relationship

class WeiboSpider(scrapy.Spider):
    name = "weibo"
    allowed_domains = ["m.weibo.cn"]
    start_urls = ['http://m.weibo.cn/']
    start_url = 'http://m.weibo.cn/api/container/getIndex?containerid=100103type=1&q={keyword}&page={page}'#%3D1%26q%3D  ----   =1&q=
    # hot_url = 'http://m.weibo.cn/api/container/getIndex?containerid=100103type=60&q={keyword}&page={page}'#%3D60%26q%3D  ----   =60&q=
    hot_url_keyword = 'http://m.weibo.cn/api/container/getIndex?containerid=100103type%3D60%26q%3D{keyword}&page={page}'#%3D60%26q%3D  ----   =60&q=
    hot_url = 'https://m.weibo.cn/api/container/getIndex?containerid=102803&since_id={page}'
    repost_url = 'https://m.weibo.cn/api/statuses/repostTimeline?id={id}&page={page}'
    repost_html_url = 'https://m.weibo.cn/status/{weibo_id}'
    # true_url = urllib.parse.quote(url)

    keywords= ['洪水','台风','内涝','暴雨','地震','泥石流','山体滑坡','龙卷风','自然灾害',
               '火灾','重大车辆事故','拆迁','上访','维权','化学事故','化工厂','核事故','核电厂','重大集会','演唱会','党委','政府','人大','政协','倒塌','油库','油车','加油站','煤气','毒气','杀人','东伊运','暴恐','恐怖','伊吉拉特','公共卫生事件','社会安全事件',
               '军人','假军人','退伍军人','退役士兵','退役军人','军车','飞机','舰艇','省军区','军分区','人武部','专武干部','专武部长'
               ]
    """
    生成获取热门微博Requests
    """
    def start_requests(self):
        #关键字热门微博搜索,type=0
        for keyword in self.keywords:
            yield scrapy.Request(self.hot_url_keyword.format(keyword=keyword,page=1),callback=self.hot_weibo_parse,priority=-4,
                                 meta={'keyword':keyword,'page':1,'type':0})
        #热门微博搜索,type=1
        yield scrapy.Request(self.hot_url.format(page=0), callback=self.hot_weibo_parse, priority=-4,
                             meta={'keyword':'','page': 0,'type':1})



    """
    处理获取到的热门微博
    """
    def hot_weibo_parse(self,response):
        # self.logger.debug(response)
        result = json.loads(response.text)
        type = response.meta.get('type')
        if result.get('data').get('cards'):
            print('----------------------',type)
            if type==0:#关键字搜索热门微博
                card_groups = result.get('data').get('cards')[-1].get('card_group')
            else:#热门微博
                card_groups = result.get('data').get('cards')
            for card_group in card_groups:
                if card_group.get('mblog'):
                    mblog = card_group.get('mblog')
                    origin_id = mblog.get('id')#获取每条源微博的id
                    # print('源微博id-------------------------',origin_id)
                    #访问转发接口，发起requests，获取转发该微博的其他微博
                    keyword = response.meta.get('keyword')
                    yield scrapy.Request(self.repost_url.format(id=origin_id, page=1),
                                         callback=self.repost_parse_origin, priority=-2,
                                         meta={'origin_id': origin_id, 'keyword': keyword, 'page': 1})

                    #源微博节点信息
                    weibo_item = WeiboItem()
                    weibo_field_map = {
                        'id': 'id', 'attitudes_count': 'attitudes_count', 'comments_count': 'comments_count',
                        'reposts_count': 'reposts_count', 'text': 'text', 'text_length': 'textLength',
                        'thumbnail_picture': 'thumbnail_pic', 'source': 'source',
                        'is_long_text': 'isLongText', 'created_at': 'created_at'

                    }  # raw_text不存在;user,origin,keyword,'pictures': 'pics',需要另外获取;,
                    for field, attr in weibo_field_map.items():#获取微博（源发布）
                        weibo_item[field] = mblog.get(attr)

                    if mblog.get('pics'):
                        pics = mblog.get('pics')
                        url = []
                        for pic in pics:
                            url.append(pic.get('url'))
                        weibo_item['pictures']= url
                    else:
                        weibo_item['pictures']= None

                    weibo_item['keyword'] =keyword
                    weibo_item['origin'] = origin_id
                    weibo_item['raw_text'] = re.sub(r'<[^\u4e00-\u9fa5]+>','',mblog.get('text'))
                    weibo_item['pid'] = 0 #表示为源微博

                    #获取源微博发布者信息
                    user_info = mblog.get('user')
                    user_item = UserItem()
                    user_field_map = {
                        'id': 'id', 'image': 'avatar_hd', 'name': 'screen_name', 'cover': 'cover_image_phone',
                        'description': 'description', 'follows_count': 'follow_count','fans_count': 'followers_count',
                        'gender': 'gender', 'statuses_count': 'statuses_count', 'verified': 'verified',
                        'verified_reason': 'verified_reason', 'verified_type': 'verified_type','flag':'verified_type_ext'
                    }#flag不存在
                    for field, attr in user_field_map.items():#获取源微博发布者信息
                        user_item[field] = user_info.get(attr)

                    weibo_item['user'] = user_info.get('id')


                    yield user_item  # 必须先生成用户，以便后续微博利用边关系插入
                    yield weibo_item



            page = response.meta.get('page')+1
            keyword = response.meta.get('keyword')

            #获取下一页。发起新的requests
            if page<=10:
                if type == 0:
                    yield scrapy.Request(self.hot_url_keyword.format(keyword=keyword, page=page),
                                         callback=self.hot_weibo_parse,
                                         priority=-3,
                                         meta={'keyword': keyword, 'page': page,'type':0})
                else:
                    yield scrapy.Request(self.hot_url.format(page=page),callback=self.hot_weibo_parse,priority=-3,
                                 meta={'keyword':keyword,'page':page,'type':1})

            else:
                pass

    """
    获取转发微博列表
    """
    def repost_parse_origin(self,response):

        result = json.loads(response.text)
        if result.get('ok') and result.get('data'):
            origin_id = response.meta.get('origin_id')
            page = response.meta.get('page')
            keyword = response.meta.get('keyword')
            """
            得到转发微博列表
            """
            groups = result.get('data').get('data') 
            for item in groups:
                weibo_id = item.get('id')#每条转发微博的ID
                # user_id = item.get('user').get('id')
                # created_at = item.get('created_at')
                """
                发起请求，获取每条转发微博的具体内容
                """
                yield scrapy.Request(self.repost_html_url.format(weibo_id=weibo_id),callback=self.repost_parse,priority=0,
                                     meta={'origin_id':origin_id,'keyword':keyword})
            """
            获取下一页的转发微博列表
            """
            page+=1
            yield scrapy.Request(self.repost_url.format(id=origin_id, page=page), callback=self.repost_parse_origin,priority=-1,
                                 meta={'origin_id': origin_id,  'page': page,'keyword':keyword})


    """
    获取转发微博信息
    """
    def repost_parse(self,response):
        pattern = re.compile('\$render_data\s=(.*)\[\d\]\s\|\|',re.S)
        result = re.search(pattern=pattern,string=response.text)
        result_json = json.loads(result.group(1))
        if result_json[0].get('status'):

            status = result_json[0].get('status')
            # 转发微博节点信息
            weibo_item = WeiboItem()
            weibo_field_map = {
                'id': 'id', 'attitudes_count': 'attitudes_count', 'comments_count': 'comments_count',
                'reposts_count': 'reposts_count', 'text': 'text', 'text_length': 'textLength',
                'source': 'source','raw_text':'raw_text','thumbnail_picture': 'thumbnail_pic' ,'pictures': 'pics',
                'is_long_text': 'isLongText', 'created_at': 'created_at',
                'pid':'pid'

            }  # raw_text不存在;user,origin,keyword需要另外获取
            #'thumbnail_picture': 'thumbnail_pic' ，'pictures': 'pics', 只有在源微博才存在，转发微博不含图片
            #'pid':直接转发或者转发评论为null，多次转发微博为int, 源微博为0
            for field, attr in weibo_field_map.items():  # 获取微博（源发布）
                weibo_item[field] = status.get(attr)
            keyword = response.meta.get('keyword')
            weibo_item['keyword'] = keyword
            weibo_item['origin'] = response.meta.get('origin_id')

            # 微博转发者信息
            user_info = status.get('user')
            user_item = UserItem()
            user_field_map = {
                'id': 'id', 'image': 'avatar_hd', 'name': 'screen_name', 'cover': 'cover_image_phone',
                'description': 'description', 'follows_count': 'follow_count', 'fans_count': 'followers_count',
                'gender': 'gender', 'statuses_count': 'statuses_count', 'verified': 'verified',
                'verified_reason': 'verified_reason', 'verified_type': 'verified_type', 'flag': 'verified_type_ext'
            }  # flag不存在
            for field, attr in user_field_map.items():  # 获取转发微博发布者信息
                user_item[field] = user_info.get(attr)

            weibo_item['user'] = user_info.get('id')

            yield user_item#必须先生成用户，以便后续微博利用边关系插入
            yield weibo_item

