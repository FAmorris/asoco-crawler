import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/' + '..'))
import multiprocessing
import threading
import time
import traceback

from watchdog.events import *
from watchdog.observers import Observer

import crawlprocess
from universal import settings

from logging.handlers import TimedRotatingFileHandler
import redis
from redis_connection import client

def get_log():
    log_dir = os.path.join(os.path.expanduser("~"), "json_manager", "logs")
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    logHandler = TimedRotatingFileHandler(os.path.join(log_dir, "crawler.log"),
                                          when='D',  # 以when为单位
                                          interval=3,  # 每个日志文件为interval个when
                                          backupCount=15,  # 保留15个when
                                          encoding='utf8')
    logFormat = logging.Formatter("%(levelname)s %(asctime)s %(message)s")
    logHandler.setFormatter(logFormat)
    log = logging.getLogger("crawler")  # 日志只允许在当前进程中访问
    log.addHandler(logHandler)
    log.setLevel("INFO")
    return log


class CrawlProcessInfo:
    # 用于存储爬虫进程信息，便于爬虫管理
    def __init__(self):
        self.process = None
        self.time = None


log = get_log()
crawlProcesses = dict()
REST_TIME = settings.REST_TIME  # 爬虫休息时间
# 爬虫配置的目录
TARGET_FOLDER = os.path.join(settings.BASE_DIR, "universal", 'configs')
# 文件夹监控线程
folder_observer = None
# 爬虫进程监控线程
process_watcher = None


class FileEventHandler(FileSystemEventHandler):
    '''
    监控config文件夹类。监控是否有文件创建或删除，从而开启或关闭爬虫
    '''
    def __init__(self):
        FileSystemEventHandler.__init__(self)
        # 防止一个事件发生两次，一次创建文件之后会触发两次create事件
        self.last = {
            "event": "",
            "file": "",
            "time": ""
        }

    def on_moved(self, event):
        if event.is_directory:
            print("directory moved from {0} to {1}".format(event.src_path, event.dest_path))
        else:
            print("file moved from {0} to {1}".format(event.src_path, event.dest_path))

    def on_created(self, event):
        filename = os.path.basename(event.src_path)
        if not filename.endswith(".json") or event.is_directory:
            return
        log.info('on_created<%s>' % filename)
        if self.last['event'] == 'created' and self.last['file'] == filename and time.time() - self.last['time'] < 4:
            return
        self.last['event'] = "created"
        self.last['file'] = filename
        self.last['time'] = time.time()
        release_process(filename)
        if filename not in crawlProcesses:
            crawlProcesses[filename] = CrawlProcessInfo()
        crawlProcesses[filename].process = get_process(filename)
        crawlProcesses[filename].process.start()

    def on_deleted(self, event):
        filename = os.path.basename(event.src_path)
        if not filename.endswith(".json") or event.is_directory:
            return

        log.info('on_delete <%s>' % filename)
        # 重复事件
        if self.last['event'] == "deleted" and self.last['file'] == filename and time.time() - self.last['time'] < 5:
            return
        self.last['event'] = 'deleted'
        self.last['file'] = filename
        self.last['time'] = time.time()
        release_process(filename)

    def on_modified(self, event):
        if event.is_directory:
            print("directory modified:{0}".format(event.src_path))
        else:
            print("file modified:{0}".format(event.src_path))


def get_current_process_info(crawlerName):
    # 根据爬虫名称获取爬虫信息，用于打印日志
    cur = crawlProcesses.get(crawlerName).process
    return "爬虫名称<%s>,进程ID<%s>,进程名称<%s>" % (crawlerName, cur.pid, cur.name)


def _go(name):
    # 爬虫进程运行函数，阻塞
    cli = client
    try:
        cli.set(name.rstrip(".json"), "爬虫正在运行")
        process = crawlprocess.get_crawler_process(name)
        process.start()
    except:
        with open(os.path.join(settings.EXCEPTION_DIR, name.rstrip(".json")), "w", encoding='utf8') as f:
            traceback.print_exc(file=f)
            cli.set(name.rstrip(".json"), "爬虫遭遇异常")


def get_process(name):
    if name.endswith(".json"):
        name = name[:-5]
    return multiprocessing.Process(target=_go, args=(name,))


def release_process(name):
    '''
    终止爬虫进程
    '''
    log.info("终止爬虫%s" % name)
    if name in crawlProcesses:
        if crawlProcesses[name].process.is_alive():
            log.info("终止进程:%s" % get_current_process_info(name))
            crawlProcesses[name].process.terminate()


def loadFiles():
    # 加载文件并启动爬虫
    files = os.listdir(TARGET_FOLDER)
    for i in files:
        if i in crawlProcesses:  # 如果已经有了，那就不用管了
            continue
        crawlProcesses[i] = CrawlProcessInfo()
        crawlProcesses[i].process = get_process(i)
        crawlProcesses[i].process.start()
        log.info("加载爬虫<%s>" % i)
        log.info("启动爬虫:%s" % get_current_process_info(i))


def check_re_run():
    global REST_TIME
    """
    监控爬虫休息线程
    :return:
    """
    cli = client
    # 检测进程是否在休息，如果在休息，让其休息时间++
    freq = 20  # 每隔20s检测一次
    try:
        while 1:
            crawlInterval = cli.get("crawlInterval")
            if crawlInterval:
                REST_TIME = int(crawlInterval)
            time.sleep(freq)
            # 如果文件已经不存在了，那就删除之
            to_remove = []
            for i in crawlProcesses:
                if not os.path.exists(os.path.join(TARGET_FOLDER, i)):
                    release_process(i)
                    to_remove.append(i)
                    log.info("%s不见了，需要移除此进程" % i)
            for i in to_remove:
                del crawlProcesses[i]
            loadFiles()  # 加载没有看见过的
            for i, v in crawlProcesses.items():
                if not v.process.is_alive():
                    v.time = 0 if v.time is None else v.time + freq
                    if v.time > REST_TIME:
                        v.time = 0
                        v.process = get_process(i)
                        v.process.start()
                        log.info("启动爬虫:%s" % get_process(i))
                    else:
                        cli.set(i.rstrip(".json"), "正在休息...")
                else:
                    cli.set(i.rstrip(".json"), "正在爬...")
    except Exception as e:
        log.error(e)
        return


def init():
    global folder_observer, process_watcher
    loadFiles()
    observer = Observer()
    event_handler = FileEventHandler()
    observer.schedule(event_handler, TARGET_FOLDER, True)
    re_run_thread = threading.Thread(target=check_re_run)
    folder_observer = observer
    process_watcher = re_run_thread


def start():
    if folder_observer is None:
        init()
    folder_observer.start()
    process_watcher.start()


def stop_all():
    folder_observer.stop()
    process_watcher.terminate()
    for i in crawlProcesses.values():
        if i.process.is_alive():
            i.process.terminate()


if __name__ == "__main__":
    print("watcher started")
    start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_all()
