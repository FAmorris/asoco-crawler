from .proxypool.scheduler import Scheduler
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    """
    代理池入口
    :return:
    """
    try:
        s = Scheduler()
        s.run()
    except:
        main()


if __name__ == '__main__':
    main()
