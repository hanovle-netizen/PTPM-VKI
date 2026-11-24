from abc import ABC, abstractmethod


class Notifier(ABC):
    """Интерфейс сторонней зависимости (отправка результата)."""

    @abstractmethod
    def send(self, message):
        """Отправляет строку; возвращает True при успехе."""


class FakeEmailNotifier(Notifier):
    """Имитация отправки на email-сервер: данные никуда не уходят."""

    def __init__(self):
        self.sent = []

    def send(self, message):
        self.sent.append(message)
        return True
