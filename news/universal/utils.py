from os.path import realpath, dirname
import json
import re
import time
import requests
from datetime import datetime

import requests
from universal.process_html import filter_tags
from scrapy import Selector

def get_config(name):
    '''
    获取json配置文件
    :param name: 
    :return: 
    '''
    path = dirname(realpath(__file__)) + '/configs/' + name + '.json'
    with open(path, 'r', encoding='utf-8') as f:
        return json.loads(f.read())

# 用于处理爬取时某个Item信息的辅助函数
# 如果需要扩展，可自行添加
def cut_from_tail(s,been):
    return s[:been];


def padtime_for_caogen(s,t):
    return s + '' + t;

def get_hits_for_clubchina(jsurl ):
    headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
            "authorization": "oauth c3cef7c66a1843f8b3a9e6a1e3160e20"
        }
    response_js = requests.get(jsurl, headers=headers)
    hit = re.findall('hits=(.*?);', response_js.text)[0]
    return hit;

def list2str(list):
    """
    列表拼合成字符串
    :param result: 列表
    :return: 字符串
    """
    return ''.join(list)


def unescape(string):
    """
    转义还原
    :param string: 被转义字符
    :return: 原字符
    """
    return re.sub('\\\\', '\\', string)


def date_transform(datetime, format_from, format_to):
    """
    时间格式转换
    :param datetime: 当前时间
    :param format_from: 当前时间格式
    :param format_to: 转后时间格式
    :return: 转后时间
    """
    if not datetime:
        return datetime
    datetime = datetime.lstrip().rstrip()
    timestamp = time.mktime(time.strptime(datetime, format_from))
    return time.strftime(format_to, time.localtime(timestamp))

def set_value(obj, value):
    """
    设置固定数值
    :param value: 数值
    :return: 数值
    """
    return value

def get_attr(obj, attr):
    """
    获取属性
    :param obj: 对象
    :param attr: 属性
    :return: 属性值
    """
    return getattr(obj, attr)

def get_time(obj, format='%Y-%m-%d %H:%M:%S'):
    """
    获取当前时间
    :param obj: 对象
    :param format: 格式
    :return: 格式化后时间
    """
    return time.strftime(format, time.localtime(time.time()))

def get_first(theList):
    if (type(theList) == list):
        if(len(theList) >= 1):
            return theList[0];
    else:
        return theList;

def get_item_from_list(theList , index):
    if len(theList) > index:
        return theList[index];
def get_content(url=None):
    """
    获取人民网bbs的帖子内容
    :param url: content的路径
    :return: content
    """
    if not url:
        return ''
    response = requests.get(url)
    if response.status_code == 200:
        content = str(response.content, encoding='utf-8')
        content = filter_tags(content)
        return content
    else:
        return ''

def get_browser_count(body_selector):
    browse_count_original_url = 'http://post.blogchina.com/addBrowseCount'
    aid = body_selector.xpath('input[@id="aid"]/@value').extract_first()
    user_id = body_selector.xpath('input[@id="user_id"]/@value').extract_first()
    if aid and user_id:
        url = browse_count_original_url + '?aid=' + str(aid) + \
              '&user_id=' + str(user_id) + '&type=click&incr=y&_=' + str(int(round(time.time() * 1000)))
        r = requests.get(url)
        num = eval(r.text)['data']['num']
        return num
    else:
        return 0

def get_bbs_info(header_info, index):
    if not header_info:
        return None
    info = header_info.extract()[int(index)].rstrip()[3:]
    return info

def set_default_values(values,index):
    """
    author: @dlx
    输入response获取的值，在存入item之前设置缺省值，如果为空，设置缺省值，不为空返回原值
    :param values: 将要存入item的值
    :param index: 标记，哪一个item项
    :return: 原值或者缺省值
    """
    if values:
        return values
    else:
        if index == "title":
            return "无题"
        elif index == "url":
            return "http://bbs.voc.com.cn/forum-76-1.html"
        elif index == "publish_time":
            today = date.today()
            today_s = today.strftime("%Y-%m-%d")
            return "发表时间："+today_s+" 00:00:00"
        elif index == "hot":
            return "0"
        elif index == "replies":
            return "0"
        elif index == "content":
            return "无内容"
        elif index == 'author':
            return "无名"
        elif index == "publish_time2":
            today = date.today()
            today_s = today.strftime("%Y/%m/%d")
            return "发表时间：" + today_s + " 00:00:00"
        else:
            return "None"

def set_default_source_chinadaily(source):
    """
    author: @chd
    :param source: 作者和来源混合的字符串
    :return: 返回来源
    """
    return re.sub(".*来源：", "", source)

def set_default_author_chinadaily(author):
    """
    author: @chd
    :param author: 作者和来源混合的字符串
    :return: 返回作者
    """
    if("作者" not in author):
        return None
    author = re.sub("来源：.*", "", author).strip()
    return re.sub(".*作者：", "", author)

def set_default_time_military(timestr):
    """
    author: @chd
    :param timestr: 时间和来源混合的字符串
    :return: 返回时间
    """
    timestr = timestr.replace("\n", "").strip()
    timestr = re.sub("[^0-9:\s-]", "", timestr).strip()
    return timestr

def set_default_time(header_info=None):
    if not header_info:
        return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    else:
        return header_info


if __name__ == '__main__':
    print(set_default_time())

def set_default_source_military(source):
    """
    author: @chd
    :param source: 时间和来源混合的字符串
    :return: 返回来源
    """
    source = source.replace("\n", "").strip()
    source = re.sub("[0-9:\s-]", "", source).strip()
    return source

def sub(video_url):
    video_url = video_url.replace(";","").strip()
    return video_url
