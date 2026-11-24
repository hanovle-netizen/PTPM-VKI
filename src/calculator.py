from src.my_project import calculate_triangle


class TriangleCalculator:
    """Класс вычислений: оборачивает метод calculate_triangle из ЛР1."""

    NOT_TRIANGLE = "не треугольник"
    INVALID_INPUT = "ошибка ввода"

    def calculate(self, side_a, side_b, side_c):
        """Возвращает (тип, сообщение_об_ошибке). Сообщение пустое, если ошибки нет."""
        triangle_type, coordinates = calculate_triangle(side_a, side_b, side_c)
        if coordinates[0] == (-2, -2):
            return self.INVALID_INPUT, "введены нечисловые данные"
        if coordinates[0] == (-1, -1):
            return self.NOT_TRIANGLE, "стороны не образуют треугольник"
        return triangle_type, ""
