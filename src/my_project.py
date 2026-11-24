import logging
import math

FIELD_SIZE = 100  # размер поля для отрисовки 100x100 px


def parse_side(value):
    """Переводит строку в float. Возвращает None, если это не число."""
    try:
        number = float(str(value).strip().replace(",", "."))
    except (ValueError, TypeError):
        return None
    if not math.isfinite(number):  # nan и inf тоже считаем не числами
        return None
    return number


def get_triangle_type(a, b, c):
    """Определяет вид треугольника по трём сторонам."""
    tol = 1e-6 * max(a, b, c)

    def eq(x, y):
        return math.isclose(x, y, rel_tol=0.0, abs_tol=tol)

    if eq(a, b) and eq(b, c):
        return "равносторонний"
    if eq(a, b) or eq(b, c) or eq(a, c):
        return "равнобедренный"
    return "разносторонний"


def get_coordinates(a, b, c):
    """Считает координаты вершин и вписывает треугольник в поле 100x100."""
    # Вершина A в (0, 0), вершина B на оси X в (c, 0),
    # вершина C по теореме косинусов (|AC| = b, |BC| = a)
    x3 = (b ** 2 + c ** 2 - a ** 2) / (2 * c)
    y3 = math.sqrt(max(b ** 2 - x3 ** 2, 0))
    points = [(0.0, 0.0), (c, 0.0), (x3, y3)]

    # Сдвигаем, чтобы не было отрицательных координат
    min_x = min(p[0] for p in points)
    points = [(x - min_x, y) for x, y in points]

    # Масштабируем, чтобы треугольник поместился в поле
    width = max(p[0] for p in points)
    height = max(p[1] for p in points)
    scale = FIELD_SIZE / max(width, height) if max(width, height) > 0 else 1.0
    return [(int(round(x * scale)), int(round(y * scale))) for x, y in points]


def calculate_triangle(side_a, side_b, side_c):
    """Главный метод: возвращает (вид треугольника, список координат)."""
    params = f"A='{side_a}', B='{side_b}', C='{side_c}'"
    logging.debug(f"Получен запрос: {params}")

    try:
        a, b, c = parse_side(side_a), parse_side(side_b), parse_side(side_c)

        # Нечисловые данные
        if a is None or b is None or c is None:
            result = ("", [(-2, -2)] * 3)
            logging.error(
                f"Неуспешный запрос: {params} | Ошибка: введены нечисловые данные | Результат: {result}"
            )
            return result

        # Отрицательные стороны или ноль
        if a <= 0 or b <= 0 or c <= 0:
            result = ("не треугольник", [(-1, -1)] * 3)
            logging.error(
                f"Неуспешный запрос: {params} | Ошибка: стороны должны быть больше нуля | Результат: {result}"
            )
            return result

        # Неравенство треугольника с согласованным допуском
        tol = 1e-6 * max(a, b, c)
        if a + b - c <= tol or a + c - b <= tol or b + c - a <= tol:
            result = ("не треугольник", [(-1, -1)] * 3)
            logging.error(
                f"Неуспешный запрос: {params} | Ошибка: не выполняется неравенство треугольника | Результат: {result}"
            )
            return result

        # Успешный случай
        result = (get_triangle_type(a, b, c), get_coordinates(a, b, c))
        logging.debug(f"Успешный запрос: {params} | Результат: {result}")
        return result

    except Exception:
        # logging.exception сам добавляет traceback
        logging.exception(f"Неуспешный запрос: {params} | Непредвиденная ошибка")
        return ("", [(-2, -2)] * 3)
