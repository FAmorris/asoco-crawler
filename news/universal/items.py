# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class NewsItem(Item):
    
    table = 'portal'
    
    url = Field()
    website = Field()
    crawl_time = Field()
    publish_time = Field()
    source = Field()
    source_url = Field()
    title = Field()
    content = Field()
    hot = Field()
    hits = Field()
    replies = Field()
    author = Field()


class PostItem(Item):#论坛
    table = 'education'
    
    url = Field()
    website = Field()
    crawl_time = Field()
    publish_time = Field()
    title = Field()
    content = Field()
    hot = Field()
    hits = Field()
    replies = Field()
    author = Field()


class BlogItem(Item):
    table = 'blogs'
    
    url = Field()
    website = Field()
    crawl_time = Field()
    publish_time = Field()
    title = Field()
    content = Field()
    hot = Field()
    hits = Field()
    replies = Field()
    author = Field()

class VideoItem(Item):
    table = 'videos'

    title = Field()
    video = Field()
    video_url = Field()
    source = Field()
    author = Field()
    publish_time = Field()
    content = Field()
    crawl_time = Field()
    url = Field()
