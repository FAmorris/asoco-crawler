## WeiboSpider

newest_weibo：为热门微博搜索

weibo_distribute：为关键词搜索热门微博


在分布式部署时，爬虫的主体weibo.py，mweibo.py中的start_requests函数均只需在一台机子上部署，用来产生

初始化种子，其余机子部署时需要注释掉该部分。

微博爬虫

