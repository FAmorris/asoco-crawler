import os

import json
import shutil
import traceback
import jsonschema
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
import logging
from json_manager import settings
import redis
from redis_connection import client
from weibo_new import watch
schema = json.load(open(settings.SCHEMA_JSON, encoding='utf8'))

log = logging.getLogger('user_op')


def admin(req):
    # manage页面
    msg = req.session.get('msg', '')
    if 'msg' in req.session:
        del req.session['msg']
    return render(req, "index.html", {
        'jsonlist': files(),
        'msg': msg,
        'sideCollapse': "side-collapse" if req.COOKIES.get("side-collapse", "no") == "yes" else ""
    })


def edit(req, filename):
    # 编辑页面
    log.info('编辑《%s》' % filename)
    editor = req.COOKIES.get('editor', "jsoneditor")
    return render(req, "edit.html" if editor == "treema" else "edit2.html", {
        'filename': filename + ".json",
        'sideCollapse': "side-collapse" if req.COOKIES.get("side-collapse", "no") == "yes" else ""
    })


def read_content(req):
    # ajax读取文件内容
    filename = req.GET['filename']
    log.info('读取文件内容《%s》' % filename)
    full_path = find_file(filename)
    if not full_path: return
    with open(full_path, encoding='utf8') as f:
        resp = HttpResponse(f.read(), content_type="application/json")
        return resp
    resp = HttpResponse()
    resp.status_code = 500
    return resp


def do_no_use(req):
    # 禁用json文件
    filename = req.POST['filename']
    log.info("禁用《%s》" % filename)
    full_path = find_file(filename, [settings.JSON_DIR])
    if not full_path: return HttpResponse("error")
    shutil.move(full_path, os.path.join(settings.BAK_JSON_DIR, filename))
    cli = client
    cli.delete(filename.rstrip(".json"))
    return HttpResponse("ok")


def do_use(req):
    # 启用json文件
    filename = req.POST['filename']
    log.info("启用爬虫配置《%s》" % filename)
    full_path = find_file(filename, [settings.BAK_JSON_DIR])
    if not full_path: return HttpResponse("error")
    shutil.move(full_path, os.path.join(settings.JSON_DIR, filename))
    return HttpResponse("ok")


def find_file(filename, dirs=[settings.BAK_JSON_DIR, settings.JSON_DIR]):
    # 根据文件名称查找文件路径
    def find(dir):
        for i in os.listdir(dir):
            if i == filename:
                return os.path.join(dir, i)

    for i in dirs:
        ans = find(i)
        if ans:
            return ans


def files():
    cli = client

    # 返回当前json列表
    def load(foler, state):
        ans = []
        for file_name in os.listdir(foler):
            if not file_name.endswith(".json"):
                continue
            item = dict()
            file_path = os.path.join(foler, file_name)
            try:
                with open(file_path, encoding='utf8') as f:
                    file_content = json.load(f)
            except:
                simpleName = file_name.rstrip(".json")
                log.info("爬虫配置文件加载异常《%s》" % file_name)
                cli.set(simpleName, "爬虫加载异常")
                with open(os.path.join(settings.EXCEPTION_PATH, simpleName), "w", encoding='utf8') as except_file:
                    traceback.print_exc(file=except_file)
                file_content = {
                    'website': '',
                    'index': '',
                    'name': '',
                    'simpleName': ''
                }
            item['website'] = file_content.get('website', file_content.get('description', ''))
            item['index'] = file_content['index']
            item['name'] = file_name
            simpleName = file_name.rstrip("json")
            item['simpleName'] = simpleName[0:-1]
            item['state'] = state
            item['lastAccessTime'] = os.path.getmtime(file_path)
            if item['index'] and not item['index'].startswith("http"):
                item['index'] = "http://" + item['index']
            if state:
                msg = cli.get(simpleName)
            else:
                msg = None
            item['message'] = str(msg, encoding='utf8') if msg else ""
            ans.append(item)
        return ans

    in_use = load(settings.JSON_DIR, True)
    if not os.path.exists(settings.BAK_JSON_DIR):
        os.mkdir(settings.BAK_JSON_DIR)
    no_use = load(settings.BAK_JSON_DIR, False)
    ans = in_use + no_use
    ans = sorted(ans, key=lambda x: -x['lastAccessTime'])
    return ans


def delete(req):
    # 删除json文件
    filename = req.GET['filename']
    log.info("删除爬虫配置《%s》" % filename)
    fullpath = find_file(filename)
    os.remove(fullpath)
    return HttpResponseRedirect("manage")


def addfile(req):
    # 添加文件
    myFile = req.FILES.get("fileToUpload")  # 获取上传的文件，如果没有文件，则默认为None
    if myFile is None:
        req.session['msg']="请添加文件！"
        return HttpResponseRedirect("manage")
    log.info("添加爬虫配置《%s》" % myFile.name)
    content = str(myFile.read(), encoding='utf8')
    filepath = os.path.join(settings.JSON_DIR, myFile.name)
    filepath2 = os.path.join(settings.BAK_JSON_DIR, myFile.name)
    msg = "添加成功！"
    if os.path.exists(filepath):
        msg = "文件名为{file}的文件已存在".format(file=myFile.name)
        log.info("addfile" + msg)
    elif os.path.exists(filepath2):
        msg = "文件名为{file}的文件已存在".format(file=myFile.name)
        log.info("addfile" + msg)
    else:
        try:
            msg="添加成功！"
            configJSON = json.loads(content)
            res = jsonschema.validate(configJSON, schema)
            with open(filepath2, mode='w', encoding='utf8') as f:  # 打开特定的文件进行二进制的写操作
                f.write(content)
        except json.JSONDecodeError:
            msg = "上传的文件不是JSON格式"
        except Exception as e:
            msg="配置文件有错误"
            log.error(e)
            traceback.print_exc()
    req.session['msg'] = msg
    return HttpResponseRedirect("manage")


def savefile(req):
    # ajax保存请求
    try:
        oldfilename = req.POST['oldFilename']
        filename = req.POST['filename']
        content = req.POST['content']
        # 新建文件或者更改文件内容（不更改文件名称）
        if oldfilename == filename or oldfilename.startswith('untitle') or oldfilename == "":  # 只更改文件内容不更改文件名
            fullpath = find_file(filename)
            if fullpath is None:  # 如果没有这个文件，那就相当于新建一个文件
                fullpath = os.path.join(settings.JSON_DIR, filename)
            with open(fullpath, "w", encoding='utf8') as f:
                f.write(content)
            log.info("保存爬虫配置《%s》" % filename)
            return HttpResponse("ok")
        else:  # 相当于重命名
            log.info("保存爬虫配置《%s（原名%s）》" % (filename, oldfilename))
            old_fullpath = find_file(oldfilename)
            fullpath = find_file(filename)
            if fullpath is None:  # 如果没有这个文件，那就相当于新建一个文件
                fullpath = os.path.join(settings.JSON_DIR, filename)
            if old_fullpath and fullpath:
                shutil.move(old_fullpath, fullpath)
            with open(fullpath, "w", encoding='utf8') as f:
                f.write(content)
        return HttpResponse("ok")
    except:
        return HttpResponse("保存失败！")


def config(req):
    # 将爬虫间隔写入settings
    crawlInterval = "7200"
    if os.path.exists(os.path.join(settings.HOME, "settings.json")):
        try:
            with open(os.path.join(settings.HOME, "settings.json"), encoding='utf8') as f:
                data = json.load(f)
                crawlInterval = data['crawlInterval']
        except:
            os.remove(os.path.join(settings.HOME, "settings.json"))
    return render(req, "config.html", {
        'sideCollapse': "side-collapse" if req.COOKIES.get("side-collapse", "no") == "yes" else "",
        "crawlInterval": crawlInterval
    })


def seelog(req):
    # 查看爬虫日志
    filename = req.GET['filename']
    simplename = filename.rstrip(".json")
    excep_path = os.path.join(settings.EXCEPTION_PATH, simplename)
    if not os.path.exists(excep_path):
        return HttpResponse(filename + "一切正常")
    else:
        with open(excep_path, encoding='utf8') as f:
            content = f.read()
        return HttpResponse(content)


def setCrawlInterval(req):
    # 设置爬虫休息间隔
    cli = client
    data = dict()
    if os.path.exists(os.path.join(settings.HOME, "settings.json")):
        try:
            with open(os.path.join(settings.HOME, "settings.json"), encoding='utf8') as f:
                data = json.load(f)
        except:
            os.remove(os.path.join(settings.HOME, "settings.json"))
    crawlInterval = int(req.POST.get("crawlInterval", "7200"))
    cli.set("crawlInterval", crawlInterval)
    data["crawlInterval"] = crawlInterval
    with open(os.path.join(settings.HOME, "settings.json"), mode="w", encoding='utf8') as f:
        json.dump(data, f)
        return HttpResponse("时间设置成功")
    return HttpResponse("时间设置失败")


def do_use_weibo(req):
    # 开启微博爬虫
    watch.start()
    log.info("启用weibo爬虫")
    return HttpResponse("ok")


def do_not_use_weibo(req):
    # 关闭微博爬虫
    watch.stop()
    log.info("停止weibo爬虫")
    return HttpResponse('ok')


def weibo_page(req):
    # 渲染微博爬虫页面
    return render(req, "weibo.html", {
        'weibostate': watch.is_use(),
        'weibo_run_state': watch.get_state(),
        'sideCollapse': "side-collapse" if req.COOKIES.get("side-collapse", "no") == "yes" else ""
    })
