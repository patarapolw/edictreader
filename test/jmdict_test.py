from time import time
from edictreader.dict import JMdict


def main():
    start = time()
    d = JMdict()
    end = time()
    print('__init__() takes {:.4f} seconds'.format(end - start))

    start = time()
    d.load_query('japanese')
    end = time()
    print('load_query() takes {:.4f} seconds'.format(end - start))

    start2 = time()
    print(list(d.search({'japanese': '鼹鼠'})))
    end2 = time()
    print('search() takes {:.4f} seconds'.format(end2 - start2))


if __name__ == '__main__':
    main()
