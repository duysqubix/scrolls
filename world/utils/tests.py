import unittest
import json
import numpy as np

from world.utils.utils import DBDumpEncoder


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
