"""Главное окно программы."""

class MainWindow:
    def __init__(self, title: str) -> None:
        self.title = title
        self.active_screen = "menu"

    def show(self) -> None:
        print(f"Запуск окна: {self.title}")
