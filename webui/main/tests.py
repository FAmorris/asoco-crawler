# Create your tests here.
"""
测试运行方法：
1、运行web服务器
2、执行py.test tests.py 命令执行此测试文件
"""

import json
import re

import requests
from  pyquery import PyQuery as pq

from main import views

host = "localhost"
port = 8000
base_url = "http://{host}:{port}/".format(host=host, port=port)

"""
测试页面
"""


def test_admin():
    """
    测试爬虫列表页面
    :return:
    """
    resp = requests.get(base_url + "manage")
    resp.encoding = 'utf8'
    res = re.findall("\w+\.json", resp.text)
    assert len(res)
    assert resp.status_code == 200


def test_config():
    """
    测试系统配置页面
    :return:
    """
    resp = requests.get(base_url + "config")
    resp.encoding = "utf8"
    html = pq(resp.text)
    assert html(".radio-img")("img").length == 2  # 断言有两个编辑器可供选择
    assert resp.status_code == 200


def test_jsoneditor():
    """
    测试JSON编辑页面
    :return:
    """
    resp = requests.get(base_url + "edit/zjmzEdu")
    resp.encoding = 'utf8'
    assert resp.status_code == 200


"""
测试API接口
"""


def test_files():
    """
    测试获取爬虫配置列表
    :return:
    """
    res = views.files()
    for i in res:
        for attr in "lastAccessTime message website index state name simpleName".split():
            assert attr in i
    assert len(res) > 0


def test_readcontent():
    """
    测试获取爬虫配置JSON的内容
    :return:
    """
    resp = requests.get(base_url + "readContent", params={
        "filename": "zjmzEdu.json"
    })
    resp.encoding = "utf8"
    data = json.loads(resp.text)
    for attr in "spider website type index".split():
        assert attr in data


def test_do_use():
    """
    测试启用爬虫
    :return:
    """
    resp = requests.post(base_url + "doUse", data={
        "filename": "zjmzEdu.json"
    })
    resp.encoding = "utf8"
    assert resp.text == "ok"


def test_do_not_use():
    """
    测试禁用爬虫
    :return:
    """
    resp = requests.post(base_url + "doNotUse", data={
        "filename": "zjmzEdu.json"
    })
    resp.encoding = "utf8"
    assert resp.text == "ok"


def test_addfile():
    """
    测试创建文件
    :return:
    """
    # 创建文件
    resp = requests.post(base_url + "addfile", files={
        "fileToUpload": ("haha.json", open(__file__, encoding='utf8'))
    })
    assert resp.status_code == 200


def test_delete():
    """
    测试删除文件
    此动作比较危险，需要手工测试
    :return:
    """
    resp = requests.get(base_url + "delete", params={
        "filename": "baga.json"
    })
    assert resp.status_code == 200


def test_savefile():
    """
    测试保存文件，此动作直接通过浏览器测试
    :return:
    """
    pass


def test_seelog():
    """
    测试查看爬虫日志
    :return:
    """
    resp = requests.get(base_url + "seelog", params={
        "filename": "zjmzEdu.json"
    })
    resp.encoding = 'utf8'
    assert resp.status_code == 200


def test_setCrawlInterval():
    """
    测试设置爬虫休息时间
    :return:
    """
    resp = requests.post(base_url + "setCrawlInterval", params={
        "crawlInterval": 7200
    })
    resp.encoding = "utf8"
    assert resp.status_code == 200
    assert resp.text == "时间设置成功"
