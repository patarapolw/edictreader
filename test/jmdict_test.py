from edictreader.dict import JMdict
from time import time

if __name__ == '__main__':
    start = time()
    d = JMdict()
    end = time()

    # for entry in d:
    #     print(entry)

    start2 = time()
    print(list(d.search({'japanese': '鼹鼠'})))
    end2 = time()

    print('__init__() takes {:.4f} seconds'.format(end-start))
    print('search() takes {:.4f} seconds'.format(end2-start2))
