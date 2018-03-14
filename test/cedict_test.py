from edictreader.dict import Cedict
from time import time

if __name__ == '__main__':
    start = time()
    d = Cedict()
    end = time()

    for entry in d:
        if 'english' in entry.keys():
            print(entry['english'])

    start2 = time()
    print(list(d.search({'simplified': '一点'})))
    end2 = time()

    print('__init__() takes {:.4f} seconds'.format(end-start))
    print('search() takes {:.4f} seconds'.format(end2-start2))
