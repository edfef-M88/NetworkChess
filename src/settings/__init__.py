"""Настройки и конфигурация приложения.

Пакет содержит константы и параметры по умолчанию, которые используются
в разных подсистемах (UI/сеть/режимы игры).

Exports:
    DEFAULT_THEME: Тема оформления по умолчанию.
    DEFAULT_TIME_CONTROL: Контроль времени по умолчанию.
    ALLOW_SPECTATORS: Разрешены ли зрители в сетевых комнатах.
"""

from .game_settings import (
    DEFAULT_THEME,
    DEFAULT_TIME_CONTROL,
    ALLOW_SPECTATORS,
)

__all__ = [
    'DEFAULT_THEME',
    'DEFAULT_TIME_CONTROL',
    'ALLOW_SPECTATORS',
]
