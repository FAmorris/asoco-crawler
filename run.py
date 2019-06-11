from multiprocessing import Process
from proxy.run import main
import os
from config import FRONT_END_PORT

def run_spider():
    """
    运行爬虫主程序
    :return:
    """
    front_end_cmd="pipenv run python webui/manage.py runserver 0.0.0.0:{port} --noreload".format(port=FRONT_END_PORT)
    os.system(front_end_cmd)
    

if __name__ == '__main__':
    # 运行爬虫
    process = Process(target=run_spider())
    process.start()
