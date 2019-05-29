from multiprocessing import Process
from proxy.run import main
import os
from config import FRONT_END_PORT


def run_proxy():
    main()


if __name__ == '__main__':
    p1 = Process(target=run_proxy)
    p1.start()