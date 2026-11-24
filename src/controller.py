class Controller:
    """Сквозной сценарий: ввод -> БД или вычисление -> отправка -> результат.

    run() возвращает None, если пользователь вышел из программы."""

    def __init__(self, calculator, database, user_input, notifier):
        self.calculator = calculator
        self.database = database
        self.user_input = user_input
        self.notifier = notifier

    def run(self):
        sides = self.user_input.get_sides()
        if sides is None:  # пользователь выбрал выход
            return None
        side1, side2, side3 = sides

        record = self.database.get(side1, side2, side3)
        if record is None:
            triangle_type, error = self.calculator.calculate(side1, side2, side3)
            self.database.add(side1, side2, side3, triangle_type, error)
        else:
            triangle_type, error = record

        result = f"{triangle_type}: {error}" if error else triangle_type
        self.notifier.send(result)
        return result
