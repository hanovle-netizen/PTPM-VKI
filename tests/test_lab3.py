import logging
import unittest
from unittest.mock import MagicMock, patch

from src.calculator import TriangleCalculator
from src.controller import Controller
from src.database import TriangleDatabase
from src.notifier import FakeEmailNotifier, Notifier
from src.user_input import ConsoleUserInput, UserInput


def setUpModule():
    logging.disable(logging.CRITICAL)  # логи ЛР1 не нужны в выводе тестов


def tearDownModule():
    logging.disable(logging.NOTSET)


def make_controller(test_case, sides, calculator=None, database=None, notifier=None):
    user_input = MagicMock(spec=UserInput)
    user_input.get_sides.return_value = sides
    if database is None:
        database = TriangleDatabase()
        test_case.addCleanup(database.close)
    return Controller(
        calculator or TriangleCalculator(),
        database,
        user_input,
        notifier or MagicMock(spec=Notifier),
    )


class TestCalculator(unittest.TestCase):
    def setUp(self):
        for name in ("logging.error", "logging.exception"):
            patcher = patch(name)
            patcher.start()
            self.addCleanup(patcher.stop)
        self.calc = TriangleCalculator()

    def test_calculator_reports_errors(self):
        self.assertEqual(self.calc.calculate("x", 1, 1),
                         ("ошибка ввода", "введены нечисловые данные"))
        self.assertEqual(self.calc.calculate(0, 1, 1)[0], "не треугольник")
        self.assertEqual(self.calc.calculate(1, 2, 3),
                         ("не треугольник", "стороны не образуют треугольник"))
        self.assertEqual(self.calc.calculate(float("nan"), 1, 1)[0], "ошибка ввода")

    def test_fractional_sides_with_float_rounding_errors(self):
        self.assertEqual(self.calc.calculate(0.1, 0.1, 0.1), ("равносторонний", ""))
        self.assertEqual(self.calc.calculate(0.1 + 0.2, 0.3, 0.3), ("равносторонний", ""))
        self.assertEqual(self.calc.calculate(0.3, 0.4, 0.5), ("разносторонний", ""))

    def test_fractional_sides_with_comma_and_exponent(self):
        self.assertEqual(self.calc.calculate("0,5", "0.5", "5e-1"), ("равносторонний", ""))
        self.assertEqual(self.calc.calculate("1.5", "2,5", "3.5"), ("разносторонний", ""))

    def test_unexpected_error_is_reported_as_invalid_input(self):
        with patch("src.my_project.get_triangle_type", side_effect=RuntimeError("сбой")):
            self.assertEqual(self.calc.calculate(3, 4, 5)[0], "ошибка ввода")


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db = TriangleDatabase()
        self.addCleanup(self.db.close)

    def test_add_and_get_record(self):
        self.db.add(3, 4, 5, "разносторонний")
        self.assertEqual(self.db.get(3, 4, 5), ("разносторонний", ""))

    def test_get_missing_record_returns_none(self):
        self.assertIsNone(self.db.get(1, 2, 3))

    def test_add_same_sides_replaces_record(self):
        self.db.add(1, 2, 3, "не треугольник", "ошибка")
        self.db.add(1, 2, 3, "другой", "")
        self.assertEqual(self.db.get(1, 2, 3), ("другой", ""))

    def test_equivalent_number_formats_share_one_record(self):
        self.db.add("3", "4", "5", "разносторонний")
        self.assertEqual(self.db.get(3.0, "4,0", 5), ("разносторонний", ""))

    def test_non_numeric_sides_are_stored_as_text(self):
        self.db.add("a", "b", "c", "ошибка ввода", "нечисловые данные")
        self.assertEqual(self.db.get(" a", "b", "c"), ("ошибка ввода", "нечисловые данные"))

    def test_delete_removes_record(self):
        self.db.add(3, 4, 5, "разносторонний")
        self.assertTrue(self.db.delete(3, 4, 5))
        self.assertIsNone(self.db.get(3, 4, 5))
        self.assertFalse(self.db.delete(3, 4, 5))


class TestInputAndNotifier(unittest.TestCase):
    def test_console_input_reads_three_sides(self):
        with patch("builtins.input", side_effect=["3", "4", "5"]):
            self.assertEqual(ConsoleUserInput().get_sides(), ("3", "4", "5"))

    def test_console_input_returns_none_on_exit_command(self):
        for answers in (["q"], ["3", "Q"], ["3", "4", " q "]):
            with self.subTest(answers=answers), patch("builtins.input", side_effect=answers):
                self.assertIsNone(ConsoleUserInput().get_sides())

    def test_interfaces_cannot_be_instantiated(self):
        with self.assertRaises(TypeError):
            UserInput()
        with self.assertRaises(TypeError):
            Notifier()

    def test_fake_notifier_stores_message(self):
        notifier = FakeEmailNotifier()
        self.assertTrue(notifier.send("привет"))
        self.assertEqual(notifier.sent, ["привет"])


class TestControllerIntegration(unittest.TestCase):
    def test_new_data_is_calculated_saved_and_sent(self):
        notifier = MagicMock(spec=Notifier)
        db = TriangleDatabase()
        self.addCleanup(db.close)
        controller = make_controller(self, ("3", "4", "5"), database=db, notifier=notifier)

        result = controller.run()

        self.assertEqual(result, "разносторонний")
        self.assertEqual(db.get("3", "4", "5"), ("разносторонний", ""))
        notifier.send.assert_called_once_with("разносторонний")

    def test_existing_record_is_taken_from_database_without_calculation(self):
        db = TriangleDatabase()
        self.addCleanup(db.close)
        db.add("3", "4", "5", "из базы")
        calculator = MagicMock(spec=TriangleCalculator)
        controller = make_controller(self, ("3", "4", "5"), calculator=calculator, database=db)

        self.assertEqual(controller.run(), "из базы")
        calculator.calculate.assert_not_called()

    def test_error_message_is_included_in_result_and_sent(self):
        notifier = FakeEmailNotifier()
        controller = make_controller(self, ("1", "2", "3"), notifier=notifier)

        result = controller.run()

        self.assertEqual(result, "не треугольник: стороны не образуют треугольник")
        self.assertEqual(notifier.sent, [result])

    def test_exit_command_returns_none_and_sends_nothing(self):
        notifier = MagicMock(spec=Notifier)
        controller = make_controller(self, None, notifier=notifier)
        self.assertIsNone(controller.run())
        notifier.send.assert_not_called()

    def test_fractional_sides_are_cached_regardless_of_format(self):
        db = TriangleDatabase()
        self.addCleanup(db.close)
        calculator = MagicMock(wraps=TriangleCalculator())
        make_controller(self, ("0.5", "0.5", "0.5"), calculator=calculator, database=db).run()
        result = make_controller(self, ("0,5", "0,50", "5e-1"), calculator=calculator, database=db).run()
        self.assertEqual(result, "равносторонний")
        calculator.calculate.assert_called_once()

    def test_second_run_with_same_data_uses_cache(self):
        db = TriangleDatabase()
        self.addCleanup(db.close)
        calculator = MagicMock(wraps=TriangleCalculator())
        controller = make_controller(self, ("2", "2", "2"), calculator=calculator, database=db)

        first = controller.run()
        second = controller.run()

        self.assertEqual(first, second)
        calculator.calculate.assert_called_once()

    def test_full_scenario_with_patched_console_input(self):
        notifier = FakeEmailNotifier()
        db = TriangleDatabase()
        self.addCleanup(db.close)
        controller = Controller(TriangleCalculator(), db, ConsoleUserInput(), notifier)
        with patch("builtins.input", side_effect=["5", "5", "8"]):
            result = controller.run()
        self.assertEqual(result, "равнобедренный")
        self.assertEqual(notifier.sent, ["равнобедренный"])

    def test_main_loops_until_exit_command(self):
        from src.main import main
        answers = ["3", "3", "3", "3", "4", "5", "1", "2", "3", "q"]
        with patch("builtins.input", side_effect=answers), patch("builtins.print") as fake_print:
            results = main(":memory:")
        self.assertEqual(results, ["равносторонний", "разносторонний",
                                   "не треугольник: стороны не образуют треугольник"])
        fake_print.assert_any_call("Результат: разносторонний")

    def test_main_exits_immediately_on_first_q(self):
        from src.main import main
        with patch("builtins.input", side_effect=["q"]), patch("builtins.print"):
            self.assertEqual(main(":memory:"), [])


if __name__ == "__main__":
    unittest.main()
