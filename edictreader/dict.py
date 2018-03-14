import re
from lxml import etree

from edictreader.dir import database_path


class Dict:
    dict = dict()

    def __iter__(self):
        return iter(self.dict.values())

    def search(self, params=None):
        if params is None:
            return

        for k, v in params.items():
            for entry in self.dict.values():
                if type(entry[k]) is list:
                    for item in entry[k]:
                        if v in item:
                            yield entry
                else:
                    if v in entry[k]:
                        yield entry


class Cedict(Dict):
    def __init__(self, dict_path=database_path('cedict.txt')):
        self.dict = dict()
        with open(dict_path, encoding='utf8') as f:
            for id, row in enumerate(f.readlines()):
                result = re.search(r'(\w+) (\w+) \[(.+)\] /(.+)/\n', row)
                if result is not None:
                    trad, simp, pinyin, engs = result.groups()
                    self.dict[id] = {
                        'traditional': trad,
                        'simplified': simp,
                        'reading': pinyin,
                        **self._engs_parser(engs)
                    }

    @staticmethod
    def _engs_parser(engs):
        eng_list = engs.split('/')
        result = dict()
        not_eng = []

        for i, item in enumerate(eng_list):
            match = re.match('see also (.+)$', item)
            if match is not None:
                result['see_also'] = match.group()
                not_eng.append(i)
                continue

            match = re.match('see (.+)$', item)
            if match is not None:
                result['see_also'] = match.group()
                not_eng.append(i)
                continue

            match = re.match('old variant of (.+)$', item)
            if match is not None:
                result['old_variant'] = match.group()
                not_eng.append(i)
                continue

            match = re.match('variant of (.+)$', item)
            if match is not None:
                result['variant'] = match.group()
                not_eng.append(i)
                continue

            match = re.match('CL:(.+)$', item)
            if match is not None:
                result['CL'] = match.group()
                not_eng.append(i)
                continue

        eng = [x for i, x in enumerate(eng_list) if i not in not_eng]
        if eng:
            result['english'] = eng

        return result


class Edict2(Dict):
    def __init__(self, dict_path=database_path('edict2')):
        self.pos = dict()
        with open(database_path('edict-pos.txt')) as f:
            for row in f.readlines():
                k, v = row.strip().split('\t')
                self.pos[k] = v

        self.dict = dict()
        with open(dict_path, encoding='euc-jp') as f:
            for i, row in enumerate(f.readlines()):
                if i == 0:
                    continue
                japs = kanas = engs = ''
                result = re.search(r'(.+) \[(.+)\] /(.+)/\n', row)
                if result is None:
                    result = re.search(r'(.+) /(.+)/\n', row)
                    if result is not None:
                        japs, engs = result.groups()
                        kanas = japs
                else:
                    japs, kanas, engs = result.groups()

                entry = {
                    'japanese': japs.split(';'),
                    'reading': kanas.split(';'),
                    **self._engs_parser(engs)
                }

                self.dict[entry['id']] = entry

    def _engs_parser(self, engs):
        addition = dict()
        eng_list = engs.split('/')

        front, eng0 = re.match(r'(\(.+\) )*(.*)', eng_list.pop(0)).groups()
        if front is not None:
            pos = list(re.findall(r'\(([^)]+)\)', front))
            human_pos = []
            for item in pos:
                see_also = re.match('See (.+)', item)
                if see_also is not None:
                    addition.update({
                        'see_also': see_also.group().split(',')
                    })
                else:
                    human_pos.append(self.pos.setdefault(item, item))
            addition.update({
                'pos': human_pos
            })

            if 'Ent' in eng_list[-1]:
                addition.update({
                    'id': eng_list.pop(-1)
                })

        return {
            'english': [eng0] + eng_list,
            **addition
        }


class JMdict(Dict):
    def __init__(self, dict_path=database_path('JMdict_e')):
        with open(dict_path) as f:
            self.root = etree.parse(f)

        self.dict = dict()
        for entry in self:
            self.dict[entry['id']] = entry

    def __iter__(self):
        return (self._dict_result(x) for x in self.root.iter('entry'))

    @staticmethod
    def _dict_result(entry):
        result = {
            'id': next(entry.iter('ent_seq')).text,
            'japanese': [x.text for x in entry.xpath('k_ele/keb')],
            'reading': [x.text for x in entry.xpath('r_ele/reb')],
            'pos': [x.text for x in entry.xpath('sense/pos')],
            'english': [x.text for x in entry.xpath('sense/gloss')]
        }
        if not result['japanese']:
            result['japanese'] = result['reading']

        return result
