from time import time
from edictreader.dict import Cedict


def test_search_simplified():
    start = time()
    d = Cedict()
    end = time()

    for entry in d:
        print(entry)

    start2 = time()
    print(list(d.search({'simplified': '一点'})))
    end2 = time()

    print('__init__() takes {:.4f} seconds'.format(end - start))
    print('search() takes {:.4f} seconds'.format(end2 - start2))


if __name__ == '__main__':
    test_search_simplified()
