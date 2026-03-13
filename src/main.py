"""Точка входа в приложение NetworkChess.

Модуль содержит функцию :func:`main`, которая инициализирует главное окно UI
и запускает отображение приложения.
"""

from src.ui.main_window import MainWindow


def main() -> None:
    """Запустить приложение.

    Создаёт экземпляр главного окна и запускает первичную отрисовку.

    Returns:
        None
    """
    app = MainWindow(title="NetworkChess")
    app.show()


if __name__ == "__main__":
    main()
