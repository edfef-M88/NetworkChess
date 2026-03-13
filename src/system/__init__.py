"""Системные сервисы NetworkChess.

Пакет объединяет прикладные сервисы, не относящиеся напрямую к отрисовке
или сетевому обмену:
- учётные записи и сессии;
- AI-движок и управление уровнем сложности 1–100;
- журналирование;
- статистика;
- сохранение/загрузка данных.

Exports:
    AccountService: Управление пользователями и сессиями.
    AIEngine: Выбор ходов для режима игры против компьютера.
    DifficultyManager: Преобразование уровня сложности в параметры AI.
    AppLogger: Единая система логирования.
    StatisticsService: Сбор и анализ статистики.
    StorageService: Работа с файловым хранилищем.
"""

from .accounts import AccountService
from .ai_engine import AIEngine
from .difficulty import DifficultyManager
from .logger import AppLogger
from .statistics import StatisticsService
from .storage import StorageService

__all__ = [
    'AccountService',
    'AIEngine',
    'DifficultyManager',
    'AppLogger',
    'StatisticsService',
    'StorageService',
]
