"""Точка входа в приложение NetworkChess."""

from src.ui.main_window import MainWindow


def main() -> None:
    app = MainWindow(title="NetworkChess")
    app.show()


if __name__ == "__main__":
    main()
