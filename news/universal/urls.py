def blog_china(front,end):
    """
    博客中国起始URL
    :param front:
    :param end:
    :return:
    """
    url="http://tuijian.blogchina.com/list/index/flag/2/channel/1/page/{page}"
    for page in range(front,end):
        yield url.format(page=page)


def chinadaily(front,end):
    """
    中国日报
    :param front:
    :param end:
    :return:
    """
    yield "http://china.chinadaily.com.cn/node_1143902.htm"
    url="http://china.chinadaily.com.cn/node_1143902_{page}.htm"
    for page in range(front,end):
        yield url.format(page=page)

def jxgov(keywords):
    """
    嘉兴政府起始URL
    :param keywords:
    :return:
    """
    url = 'http://js.jiaxing.cn:9090/was5/web/search?page=1&channelid=212055&searchword={keyword}&keyword={keyword}&perpage=100&outlinepage=1'
    for keyword in keywords:
        yield url.format(keyword=keyword)

def qq_news(page):
    """
    腾讯新闻起始URL
    :param page:
    :return:
    """
    url="http://roll.news.qq.com/interface/cpcroll.php?callback=rollback&site=news&mode=1&cata=&date=2018-01-18&page=1&_=1516279115541"
    yield url