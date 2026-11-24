import unittest

from src.converter import Converter


class TestConverter(unittest.TestCase):
    def test_zero_raises_value_error(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)

    def test_negative_zero_raises_value_error(self):
        with self.assertRaises(ValueError):
            Converter.do(-0.0)

    def test_big_positive_returns_1000(self):
        self.assertEqual(Converter.do(500.5), 1000)

    def test_upper_range_lower_bound_returns_1000(self):
        self.assertEqual(Converter.do(100.7), 1000)

    def test_just_below_upper_range_returns_integer_part(self):
        self.assertEqual(Converter.do(100.6), 100)

    def test_positive_range_returns_integer_part(self):
        self.assertEqual(Converter.do(65.7), 65)

    def test_smallest_positive_returns_zero(self):
        self.assertEqual(Converter.do(0.1), 0)

    def test_positive_integer_value_is_kept(self):
        self.assertEqual(Converter.do(1.0), 1)

    def test_small_negative_returns_integer_part_minus_five(self):
        self.assertEqual(Converter.do(-0.1), -5)

    def test_negative_range_truncates_toward_zero(self):
        self.assertEqual(Converter.do(-10.9), -15)

    def test_negative_range_lower_bound_included(self):
        self.assertEqual(Converter.do(-30.4), -35)

    def test_negative_range_upper_neighbour(self):
        self.assertEqual(Converter.do(-30.0), -35)

    def test_lower_range_upper_bound_returns_minus_2000(self):
        self.assertEqual(Converter.do(-30.5), -2000)

    def test_very_negative_returns_minus_2000(self):
        self.assertEqual(Converter.do(-94.5), -2000)

    def test_result_is_int(self):
        for x in (150.0, 5.5, -5.5, -50.0):
            with self.subTest(x=x):
                self.assertIsInstance(Converter.do(x), int)


if __name__ == "__main__":
    unittest.main()
