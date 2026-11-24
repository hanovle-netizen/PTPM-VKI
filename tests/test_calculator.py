import unittest

from selenium import webdriver

from pages.calculator_page import CalculatorPage


class CalculatorTestCase(unittest.TestCase):
    def setUp(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1280,800")
        self.driver = webdriver.Chrome(options=options)
        self.page = CalculatorPage(self.driver).open()

    def tearDown(self):
        self.driver.quit()


class TestOperations(CalculatorTestCase):
    def test_addition(self):
        self.assertEqual(self.page.calculate(2, "+", 3), "5")

    def test_subtraction(self):
        self.assertEqual(self.page.calculate(10, "-", 4), "6")

    def test_subtraction_gives_negative_result(self):
        self.assertEqual(self.page.calculate(3, "-", 10), "-7")

    def test_multiplication(self):
        self.assertEqual(self.page.calculate(6, "*", 7), "42")

    def test_division(self):
        self.assertEqual(self.page.calculate(9, "/", 2), "4.5")

    def test_decimal_addition(self):
        self.assertEqual(self.page.calculate("1.5", "+", "2.25"), "3.75")

    def test_negative_operands_multiplication(self):
        self.assertEqual(self.page.calculate(-4, "*", -5), "20")

    def test_multiplication_by_zero(self):
        self.assertEqual(self.page.calculate(123, "*", 0), "0")

    def test_large_numbers_addition(self):
        self.assertEqual(self.page.calculate(1000000, "+", 2000000), "3000000")


class TestDivisionByZero(CalculatorTestCase):
    """Приложение (AngularJS 1.0.7) не выводит Infinity/NaN и показывает null."""

    def test_positive_number_divided_by_zero_shows_null(self):
        self.assertEqual(self.page.calculate(5, "/", 0), "null")

    def test_negative_number_divided_by_zero_shows_null(self):
        self.assertEqual(self.page.calculate(-5, "/", 0), "null")

    def test_zero_divided_by_zero_shows_null(self):
        self.assertEqual(self.page.calculate(0, "/", 0), "null")


class TestInterface(CalculatorTestCase):
    def test_default_state_is_zero_plus_zero(self):
        self.assertEqual(self.page.get_result_text(), "0 + 0 = 0")

    def test_available_operations_list(self):
        self.assertEqual(self.page.get_available_operations(), ["+", "-", "*", "/"])

    def test_increment_buttons_change_both_numbers(self):
        self.page.increment_first()
        self.page.increment_first()
        self.page.increment_second()
        self.assertEqual((self.page.get_first_value(), self.page.get_second_value()), ("2", "1"))
        self.assertEqual(self.page.get_result(), "3")

    def test_decrement_buttons_change_both_numbers(self):
        self.page.decrement_first()
        self.page.decrement_second()
        self.page.decrement_second()
        self.assertEqual((self.page.get_first_value(), self.page.get_second_value()), ("-1", "-2"))
        self.assertEqual(self.page.get_result(), "-3")

    def test_buttons_work_after_manual_input(self):
        self.page.enter_first_number(10)
        self.page.increment_first()
        self.assertEqual(self.page.get_first_value(), "11")

    def test_result_updates_when_operation_changes(self):
        self.page.enter_first_number(8)
        self.page.enter_second_number(2)
        self.page.select_operation("/")
        self.assertEqual(self.page.get_result(), "4")
        self.page.select_operation("*")
        self.assertEqual(self.page.get_result(), "16")


if __name__ == "__main__":
    unittest.main()
