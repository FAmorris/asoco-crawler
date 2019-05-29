import sys

import crawlprocess

if __name__ == '__main__':
    name = sys.argv[1]
    process = crawlprocess.get_crawler_process(name)
    process.start()
