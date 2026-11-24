from abc import ABC, abstractmethod

EXIT_COMMAND = "q"


class UserInput(ABC):
    """Интерфейс получения данных от пользователя."""

    @abstractmethod
    def get_sides(self):
        """Возвращает кортеж из трёх сторон или None, если пользователь хочет выйти."""


class ConsoleUserInput(UserInput):
    def get_sides(self):
        sides = []
        for name in "ABC":
            value = input(f"Сторона {name} (q - выход): ")
            if value.strip().lower() == EXIT_COMMAND:
                return None
            sides.append(value)
        return tuple(sides)
