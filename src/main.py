from src.calculator import TriangleCalculator
from src.controller import Controller
from src.database import TriangleDatabase
from src.notifier import FakeEmailNotifier
from src.user_input import ConsoleUserInput


def main(db_path="triangles.db"):
    """Крутит сценарий в цикле до команды выхода. Возвращает список результатов."""
    database = TriangleDatabase(db_path)
    results = []
    try:
        controller = Controller(
            TriangleCalculator(), database, ConsoleUserInput(), FakeEmailNotifier(),
        )
        while True:
            print("\nВведите три стороны треугольника")
            result = controller.run()
            if result is None:
                break
            print(f"Результат: {result}")
            results.append(result)
    finally:
        database.close()
    return results


if __name__ == "__main__":  # pragma: no cover
    main()
