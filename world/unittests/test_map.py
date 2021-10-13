from unittest import TestCase
from world.map import Wormy


class TestWormy(TestCase):
    def test_calculate_map_size(self):
        x1, y1 = (5, 5)
        x2, y2 = (7, 7)

        self.assertEqual(Wormy.calculate_map_size(x1, y1), (9, 9))
        self.assertEqual(Wormy.calculate_map_size(x2, y2), (11, 11))

    def test_calculate_map_size_even_values(self):
        x, y = (4, 4)
        self.assertEqual(Wormy.calculate_map_size(x, y), (9, 9))

    def test_calculate_map_center_coordinates(self):
        self.assertEqual(Wormy.calculate_center_coordinates(5, 5), (2, 2))
        self.assertEqual(Wormy.calculate_center_coordinates(7, 7), (3, 3))

    def test_calculate_map_center_coordinates_error_no_match(self):
        x = 8
        y = 9
        self.assertRaises(ValueError, Wormy.calculate_center_coordinates, x, y)

    def test_map_grid_initialization(self):
        map_size_x, map_size_y = (5, 5)
        grid = Wormy.initialize_grid_map(map_size_x, map_size_y)

        expected_empty_grid_value = {
            'symbol': '',
            'up': False,
            'down': False,
            'south': False,
            'east': False,
            'west': False,
            'north': False
        }

        self.assertEqual(len(grid), map_size_y)
        self.assertEqual(len(grid[0]), map_size_x)
        self.assertDictEqual(expected_empty_grid_value, grid[0][0])

    def test_map_grid_distinct_grid_values(self):
        """tests to make sure grid values are identically seperate dictionaries and not references"""
        map_size_x, map_size_y = (9, 9)
        grid = Wormy.initialize_grid_map(map_size_x, map_size_y)

        grid_x_0 = grid[0][0]
        grid_x_1 = grid[0][1]
        grid_y_0 = grid[1][0]
        grid_y_1 = grid[2][0]

        self.assertIsNot(grid_x_0, grid_x_1)
        self.assertIsNot(grid_y_0, grid_y_1)
