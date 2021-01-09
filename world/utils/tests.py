import re
import unittest
import json
import numpy as np

from evennia import GLOBAL_SCRIPTS
from evennia.utils.dbserialize import deserialize
from tinydb.database import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import MemoryStorage
from world.utils.utils import DBDumpEncoder, capitalize_sentence, _LANG_TAGS, parse_dot_notation, room_exists
from world.utils.db import _search_db, search_mobdb, search_objdb, search_roomdb, search_zonedb, _RE_COMPARATOR_PATTERN


class TestNumpyToJsonEncoding(unittest.TestCase):
    """Tests the custom json encoder"""
    def test_encode_integer(self):
        x = np.int64(1)
        result = json.dumps(x, cls=DBDumpEncoder)
        self.assertEqual(str(int(x)), result)

    def test_encode_float(self):
        x = np.float64(1.0)
        result = json.dumps(x, cls=DBDumpEncoder)
        self.assertEqual(str(float(x)), result)

    def test_encode_ndarray(self):
        arr = np.array([1, 2, 3])
        result = json.dumps(arr, cls=DBDumpEncoder)

        self.assertEqual(str(arr.tolist()), result)


class TestSearchDB(unittest.TestCase):
    def setUp(self) -> None:
        self.db = TinyDB(storage=CachingMiddleware(MemoryStorage))
        data = {
            1: {
                'name': 'tavis',
                'cls': 'cleric',
                'race': 'human',
                'sdesc': 'a human cleric',
                'extra': {
                    'language': "common"
                },
                'hp': 10
            },
            2: {
                'name': 'naud',
                'cls': 'thief',
                'race': 'elf',
                'sdesc': 'an elven thief',
                'extra': {
                    'language': "elven"
                },
                'hp': 15
            },
            3: {
                'name': 'yffr',
                'cls': 'cleric',
                'race': 'elf',
                'sdesc': 'an elven cleric',
                'extra': {
                    'language': "elven"
                },
                'hp': 20
            }
        }

        self.test_table = self.db.table('test')
        for vnum, d in data.items():
            self.test_table.insert({'vnum': vnum, **d})

    def tearDown(self) -> None:
        self.db.drop_tables()
        self.db.close()

    def test_mobdb_return_all(self):
        db = deserialize(GLOBAL_SCRIPTS.mobdb.vnum)
        self.assertEqual(len(db), len(search_mobdb('all')))

    def test_objdb_return_all(self):
        db = deserialize(GLOBAL_SCRIPTS.objdb.vnum)
        self.assertEqual(len(db), len(search_objdb('all')))

    def test_zonedb_return_all(self):
        db = deserialize(GLOBAL_SCRIPTS.zonedb.vnum)
        self.assertEqual(len(db), len(search_zonedb('all')))

    def test_roomdb_return_all(self):
        db = deserialize(GLOBAL_SCRIPTS.roomdb.vnum)
        self.assertEqual(len(db), len(search_roomdb('all')))

    def test_one_keyword(self):
        expected_len = 1
        records = _search_db(db=self.test_table, name='tavis')
        self.assertEqual(len(records), expected_len)

    def test_two_keyword(self):
        records = _search_db(db=self.test_table, cls='cleric', race='elf')
        self.assertEqual(1, len(records))

    def test_extra_keyword(self):
        records = _search_db(db=self.test_table, extra="language elven")

        self.assertEqual(2, len(records))

    def test_logical_sign_for_integers(self):
        records = _search_db(db=self.test_table, hp=">=15")
        self.assertEqual(2, len(records))

    def test_between_using_logical_signs_for_integers(self):
        records = _search_db(db=self.test_table, hp='11-18')
        self.assertEqual(1, len(records))

    def test_between_using_logical_signs_edge_cases(self):
        records = _search_db(db=self.test_table, hp='10-20')
        self.assertEqual(3, len(records))

    def test_search_by_vnum(self):
        vnum = 2
        record = _search_db(db=self.test_table, vnum=vnum)
        self.assertEqual(1, len(record))

    def test_logical_comparator_pattern(self):
        pattern = _RE_COMPARATOR_PATTERN
        input = ">=15"
        expected = ["", ">=", "15"]

        result = re.split(pattern, input)
        self.assertListEqual(result, expected)

    def test_logical_comparator_pattern_cleaned(self):
        pattern = _RE_COMPARATOR_PATTERN
        input = ">=15"
        expected = [">=", "15"]

        result = re.split(pattern, input)
        self.assertListEqual(result[1:], expected)


class TestRPLanguageParser(unittest.TestCase):
    def setUp(self) -> None:
        self.text = """
        >tamrielic<
        this is the common tongue

        >aldmerish<
        hello there young one.

        >orcish<
        die now!!
        """

    def test_rplanguage_tags(self):
        num_langs = 3
        num_text = 3
        total_chunks = num_langs + num_text

        self.assertEqual(total_chunks,
                         len(re.split(_LANG_TAGS, self.text)[1:]))


class TestBasicUtils(unittest.TestCase):
    def test_capitalize_sentence(self):
        input = "hello there. my name is tavis. pleased to meet you."
        expected = "Hello there. My name is tavis. Pleased to meet you."
        self.assertEqual(expected, capitalize_sentence(input))

    def test_dot_notation_none(self):
        obj = 'book'
        self.assertEqual((None, "book"), parse_dot_notation(obj))

    def test_dot_notation_num(self):
        obj = "1.book"
        self.assertEqual((1, "book"), parse_dot_notation(obj))

    def test_dot_notation_all(self):
        obj = "all.book"
        self.assertEqual(('all', "book"), parse_dot_notation(obj))

    def test_room_exists(self):
        vnum = 1
        self.assertEqual(room_exists(vnum), True)