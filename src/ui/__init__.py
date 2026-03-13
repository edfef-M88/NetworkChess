"""Пользовательский интерфейс NetworkChess.

Пакет содержит «витрину» UI-компонентов: главное окно, меню, рендерер доски
и центр уведомлений.

Примечание: текущая реализация ориентирована на учебный проект и использует
упрощённые методы отображения (включая вывод в консоль).
"""

from .main_window import MainWindow
from .game_menu import GameMenu
from .board_renderer import BoardRenderer
from .notifications import NotificationCenter

__all__ = [
    'MainWindow',
    'GameMenu',
    'BoardRenderer',
    'NotificationCenter',
]
