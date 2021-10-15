import re
import unittest
import json
import numpy as np

from evennia import GLOBAL_SCRIPTS
from evennia.utils.dbserialize import deserialize
from world.utils.utils import DBDumpEncoder, capitalize_sentence, _LANG_TAGS, parse_dot_notation, range_intersects
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
        self.mock_db = {
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

    def test_mobdb_return_all(self):
        db = deserialize(GLOBAL_SCRIPTS.mobdb.vnum)
        self.assertDictEqual(db, search_mobdb('all'))

    def test_objdb_return_all(self):
        db = deserialize(GLOBAL_SCRIPTS.objdb.vnum)
        self.assertDictEqual(db, search_objdb('all'))

    def test_zonedb_return_all(self):
        db = deserialize(GLOBAL_SCRIPTS.zonedb.vnum)
        self.assertDictEqual(db, search_zonedb('all'))

    def test_roomdb_return_all(self):
        db = deserialize(GLOBAL_SCRIPTS.roomdb.vnum)
        self.assertDictEqual(db, search_roomdb('all'))

    def test_one_keyword(self):
        expected_len = 1
        records = _search_db(db=self.mock_db, name='tavis')
        self.assertEqual(len(records), expected_len)

    def test_two_keyword(self):
        expected = {3: self.mock_db[3]}
        records = _search_db(db=self.mock_db, cls='cleric', race='elf')
        self.assertDictEqual(expected, records)

    def test_extra_keyword(self):
        d = {2: self.mock_db[2], 3: self.mock_db[3]}
        records = _search_db(db=self.mock_db, extra="language elven")

        self.assertDictEqual(d, records)

    def test_logical_sign_for_integers(self):
        d = {2: self.mock_db[2], 3: self.mock_db[3]}
        records = _search_db(db=self.mock_db, hp=">=15")
        self.assertDictEqual(d, records)

    def test_between_using_logical_signs_for_integers(self):
        expected_record = {2: self.mock_db[2]}
        first_set = _search_db(db=self.mock_db, hp=">10")
        records = _search_db(db=first_set, hp="<20")
        self.assertDictEqual(expected_record, records)

    def test_search_by_vnum(self):
        vnum = 2
        expected_record = self.mock_db[vnum]
        record = _search_db(db=self.mock_db, vnum=vnum)
        self.assertDictEqual({vnum: expected_record}, record)

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

    def test_range_intersect_true(self):
        sample_x, sample_y = (7, 12)
        test_x_1, test_y_1 = (5, 10)
        test_x_2, test_y_2 = (4, 10)
        self.assertTrue(
            range_intersects(sample_x, sample_y, test_x_1, test_y_1))
        self.assertTrue(
            range_intersects(sample_x, sample_y, test_x_2, test_y_2))

    def test_range_intersect_true_edge_case(self):
        sample_x, sample_y = (3, 5)
        test_x, test_y = (5, 10)
        self.assertTrue(range_intersects(sample_x, sample_y, test_x, test_y))

        sample_x, sample_y = (10, 12)
        test_x, test_y = (5, 10)
        self.assertTrue(range_intersects(sample_x, sample_y, test_x, test_y))
