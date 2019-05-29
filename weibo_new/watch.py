from weibo_new.weiboprocess import get_crawler_process
import multiprocessing
import threading
import time
import sys
import os
from webui.json_manager import settings
process_rest_time = 0
def process_run():
    """
    运行爬虫进程
    :return:
    """
    pro = get_crawler_process()
    pro.start()
    print("=" * 10)


process = None
watch_thread = None


def watch():
    """
    监听现有进程
    :return:
    """
    global process_rest_time, process

    while 1:
        if watch_thread is None:
            break
        if process.is_alive():
            time.sleep(20)
        else:
            process_rest_time += 20
            if process_rest_time > settings.REST_TIME:
                process_rest_time = 0
                process = multiprocessing.Process(target=process_run)
                process.start()
    process.terminate()
    process = None


def start():
    """
    启动爬虫
    :return:
    """
    global process, watch_thread
    if process != None:
        print("none!!!!!")
        return
    process = multiprocessing.Process(target=process_run)
    process.start()
    watch_thread = threading.Thread(target=watch)
    watch_thread.start()


def stop():
    """
    关闭爬虫
    :return:
    """
    global process, watch_thread
    watch_thread = None


def get_state():
    """
    获取运行状态
    :return:
    """
    if not process:
        return "爬虫未运行"
    elif process.is_alive():
        return "爬虫正在运行"
    else:
        return "爬虫正在休息"


def is_use():
    """
    是否正运行
    :return:
    """
    if process:
        return True
    else:
        return False


if __name__ == '__main__':
    start()