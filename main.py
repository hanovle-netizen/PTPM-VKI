import logging
import math
import os
import sys

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
    if math.isclose(a, b) and math.isclose(b, c):
        return "равносторонний"
    if math.isclose(a, b) or math.isclose(b, c) or math.isclose(a, c):
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
    scale = FIELD_SIZE / max(width, height)
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
            logging.error(f"Неуспешный запрос: {params} | Ошибка: введены нечисловые данные | Результат: {result}")
            return result

        # Отрицательные стороны или ноль
        if a <= 0 or b <= 0 or c <= 0:
            result = ("не треугольник", [(-1, -1)] * 3)
            logging.error(f"Неуспешный запрос: {params} | Ошибка: стороны должны быть больше нуля | Результат: {result}")
            return result

        # Неравенство треугольника
        if a + b <= c or a + c <= b or b + c <= a:
            result = ("не треугольник", [(-1, -1)] * 3)
            logging.error(f"Неуспешный запрос: {params} | Ошибка: не выполняется неравенство треугольника | Результат: {result}")
            return result

        triangle_type = get_triangle_type(a, b, c)
        coordinates = get_coordinates(a, b, c)
        result = (triangle_type, coordinates)
        logging.info(f"Успешный запрос: {params} | Результат: {result}")
        return result

    except Exception:
        # logging.exception сам добавляет traceback
        logging.exception(f"Неуспешный запрос: {params} | Непредвиденная ошибка")
        return ("", [(-2, -2)] * 3)


def Main():
    os.makedirs("logs", exist_ok=True)  # создаём папку для логов, если её нет

    log_format = "%(asctime)s | [%(levelname)-7s] | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(
        level=logging.DEBUG,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/file_txt.log", encoding="utf-8"),
        ],
    )
    logging.info("Логгер успешно сконфигурирован")
    logging.info("Приложение запущено")

    while True:
        print("\nВведите три стороны треугольника (или q для выхода)")
        side_a = input("Сторона A: ")
        if side_a.lower() == "q":
            break
        side_b = input("Сторона B: ")
        side_c = input("Сторона C: ")

        triangle_type, coordinates = calculate_triangle(side_a, side_b, side_c)
        print(f"Вид: {triangle_type if triangle_type else '(пустая строка)'}")
        print(f"Координаты: {coordinates}")

    logging.info("Приложение завершено")


if __name__ == "__main__":
    Main()
