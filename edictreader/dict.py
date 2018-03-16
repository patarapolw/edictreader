import re
from lxml import etree
import xmltodict
from abc import ABCMeta, abstractmethod

from edictreader.dir import database_path


class Dict(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        self.dictionary = dict()

    def __iter__(self):
        return iter(self.dictionary.values())

    def search(self, params: dict, exact_match=False):
        for k, v in params.items():
            for entry in self.dictionary.values():
                if isinstance(entry[k], list):
                    for item in entry[k]:
                        if exact_match:
                            if v == item:
                                yield entry
                        else:
                            if v in item:
                                yield entry
                else:
                    if exact_match:
                        if v == entry[k]:
                            yield entry
                    else:
                        if v in entry[k]:
                            yield entry


class Cedict(Dict):
    def __init__(self, dict_path=database_path('cedict_ts.u8')):
        self.dictionary = dict()
        with open(dict_path, encoding='utf8') as f:
            for item_id, row in enumerate(f.readlines()):
                result = re.search(r'(\w+) (\w+) \[(.+)\] /(.+)/\n', row)
                if result is not None:
                    trad, simp, pinyin, engs = result.groups()
                    self.dictionary[item_id] = {
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
                result['see_also'] = match.group(1)
                not_eng.append(i)
                continue

            match = re.match('see (.+)$', item)
            if match is not None:
                result['see_also'] = match.group(1)
                not_eng.append(i)
                continue

            match = re.match('old variant of (.+)$', item)
            if match is not None:
                result['old_variant'] = match.group(1)
                not_eng.append(i)
                continue

            match = re.match('variant of (.+)$', item)
            if match is not None:
                result['variant'] = match.group(1)
                not_eng.append(i)
                continue

            match = re.match('CL:(.+)$', item)
            if match is not None:
                result['CL'] = match.group(1)
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

        self.dictionary = dict()
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

                self.dictionary[entry['id']] = entry

    def _engs_parser(self, engs):
        addition = {
            'raw': engs,
        }
        eng_list = engs.split('/')

        front, eng0 = re.match(r'(\(.+\) )*(.*)', eng_list.pop(0)).groups()
        if front is not None:
            pos = list(re.findall(r'\(([^)]+)\)', front))
            human_pos = []
            for item in pos:
                see_also = re.match('See (.+)', item)
                if see_also is not None:
                    addition.update(dict(see_also=see_also.group(1).split(',')))
                else:
                    human_pos.append(self.pos.setdefault(item, item))
            addition.update(dict(pos=human_pos))

            if 'Ent' in eng_list[-1]:
                addition.update(dict(id=eng_list.pop(-1)))

        return {
            'english': [eng0] + eng_list,
            **addition
        }


class JMdict(Dict):
    def __init__(self, dict_path=database_path('JMdict_e')):
        with open(dict_path) as f:
            self.root = etree.parse(f)

        self.query = dict()

    def __iter__(self):
        return self.root.iter('entry')

    def load_query(self, key):
        if key not in self.query.keys():
            xpath = {
                'id': 'ent_seq',
                'japanese': 'k_ele/keb',
                'reading': 'r_ele/reb',
                'pos': 'sense/pos',
                'english': 'sense/gloss',
                'misc': 'sense/misc',
                'xref': 'sense/xref',
                'field': 'sense/field'
            }.get(key)
            self.query[key] = dict()
            for entry in self:
                for item in entry.xpath(xpath):
                    self.query[key].setdefault(item.text, []).append(entry)

    def search(self, params: dict, exact_match=False):
        for k, v in params.items():
            self.load_query(k)
            if exact_match:
                if v in self.query[k]:
                    yield self.format(self.query[k][v][0])
                    # The result is always nested with multiple elements inside.
                    # e.g. [[<Element entry>, <Element entry>]]
            else:
                for item in self.query[k]:
                    if v in item:
                        yield self.format(self.query[k][v][0])

    @staticmethod
    def format(entry):
        def set_dict_pri(path1, path2, path_pri):
            return {
                'primary': entry.xpath('{}/{}/following-sibling::{}/text()'
                                       .format(path1, path2, path_pri)),
                'others': entry.xpath('{}/{}[not(following-sibling::{})]/text()'
                                       .format(path1, path2, path_pri)),
            }

        result = {
            'raw': xmltodict.parse(etree.tostring(entry))['entry'],
            'xml': etree.tostring(entry),
            'id': entry.xpath('ent_seq/text()')[0],
            'japanese': set_dict_pri('k_ele', 'keb', 'ke_pri'),
            'reading': set_dict_pri('r_ele', 'reb', 're_pri'),
            'pos': entry.xpath('sense/pos/text()'),
            'english': entry.xpath('sense/gloss/text()'),
            'misc': entry.xpath('sense/misc/text()'),
            'xref': entry.xpath('sense/xref/text()'),
            'field': entry.xpath('sense/field/text()'),
        }

        to_pop = []
        for k, v in result.items():
            if not v:
                to_pop.append(k)
        for k in to_pop:
            result.pop(k)

        if 'japanese' not in result.keys():
            result['japanese'] = result['reading']

        return result
