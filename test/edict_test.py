from edictreader.dict import Edict2
from time import time

if __name__ == '__main__':
    start = time()
    d = Edict2()
    end = time()

    # for item in d:
    #     print(item)

    start2 = time()
    print(list(d.search({'japanese': '鼹鼠'})))
    end2 = time()

    print('__init__() takes {:.4f} seconds'.format(end - start))
    print('search() takes {:.4f} seconds'.format(end2 - start2))
