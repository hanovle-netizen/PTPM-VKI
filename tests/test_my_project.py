import unittest
import unittest.mock

from src.my_project import calculate_triangle, get_triangle_type, parse_side


class TestParseSide(unittest.TestCase):
    def test_parse_side_returns_float_for_integer_string(self):
        self.assertEqual(parse_side("5"), 5.0)

    def test_parse_side_accepts_comma_as_decimal_separator(self):
        self.assertEqual(parse_side("2,5"), 2.5)

    def test_parse_side_returns_none_for_text(self):
        self.assertIsNone(parse_side("abc"))

    def test_parse_side_returns_none_for_nan_and_inf(self):
        self.assertIsNone(parse_side("nan"))
        self.assertIsNone(parse_side("inf"))

    def test_parse_side_returns_none_for_none(self):
        self.assertIsNone(parse_side(None))


class TestTriangleType(unittest.TestCase):
    def test_equilateral_triangle_is_detected(self):
        self.assertEqual(get_triangle_type(3, 3, 3), "равносторонний")

    def test_isosceles_triangle_is_detected_for_any_pair(self):
        for sides in [(3, 3, 4), (3, 4, 3), (4, 3, 3)]:
            with self.subTest(sides=sides):
                self.assertEqual(get_triangle_type(*sides), "равнобедренный")

    def test_scalene_triangle_is_detected(self):
        self.assertEqual(get_triangle_type(3, 4, 5), "разносторонний")


class TestCalculateTriangle(unittest.TestCase):
    def setUp(self):
        logging_patch = unittest.mock.patch("logging.error")
        logging_patch.start()
        self.addCleanup(logging_patch.stop)

    def test_equilateral_triangle_result(self):
        kind, _ = calculate_triangle(5, 5, 5)
        self.assertEqual(kind, "равносторонний")

    def test_isosceles_triangle_result(self):
        kind, _ = calculate_triangle(5, 5, 8)
        self.assertEqual(kind, "равнобедренный")

    def test_scalene_triangle_result(self):
        kind, _ = calculate_triangle(3, 4, 5)
        self.assertEqual(kind, "разносторонний")

    def test_string_input_is_accepted(self):
        kind, _ = calculate_triangle("3", "4", "5")
        self.assertEqual(kind, "разносторонний")

    def test_comma_decimal_input_is_accepted(self):
        kind, _ = calculate_triangle("2,5", "2,5", "2,5")
        self.assertEqual(kind, "равносторонний")

    def test_zero_side_is_not_triangle(self):
        self.assertEqual(calculate_triangle(0, 4, 5), ("не треугольник", [(-1, -1)] * 3))

    def test_negative_side_is_not_triangle(self):
        self.assertEqual(calculate_triangle(-3, 4, 5), ("не треугольник", [(-1, -1)] * 3))

    def test_degenerate_triangle_is_not_triangle(self):
        self.assertEqual(calculate_triangle(1, 2, 3)[0], "не треугольник")

    def test_violated_triangle_inequality_is_not_triangle(self):
        self.assertEqual(calculate_triangle(1, 1, 10)[0], "не треугольник")

    def test_non_numeric_input_returns_error_code(self):
        self.assertEqual(calculate_triangle("a", 4, 5), ("", [(-2, -2)] * 3))

    def test_empty_string_returns_error_code(self):
        self.assertEqual(calculate_triangle("", "", ""), ("", [(-2, -2)] * 3))

    def test_coordinates_fit_into_field(self):
        _, points = calculate_triangle(3, 4, 5)
        for x, y in points:
            self.assertTrue(0 <= x <= 100 and 0 <= y <= 100)

    def test_coordinates_have_three_points(self):
        _, points = calculate_triangle(7, 8, 9)
        self.assertEqual(len(points), 3)

    def test_right_triangle_coordinates(self):
        _, points = calculate_triangle(3, 4, 5)
        self.assertEqual(points[0], (0, 0))
        self.assertEqual(points[1], (100, 0))

    def test_very_large_sides_are_supported(self):
        kind, _ = calculate_triangle(1e9, 1e9, 1e9)
        self.assertEqual(kind, "равносторонний")

    def test_very_small_sides_are_supported(self):
        kind, _ = calculate_triangle(1e-6, 1e-6, 1e-6)
        self.assertEqual(kind, "равносторонний")


if __name__ == "__main__":
    unittest.main()
