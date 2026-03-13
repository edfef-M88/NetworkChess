"""Сетевой слой NetworkChess.

Пакет содержит клиент/сервер для сетевых партий, чат, а также компонент
проверки и «санитизации» входящих сообщений.

Важно: реализация является учебной и не претендует на полноценную
криптографическую защиту.
"""

from .client import GameClient
from .server import MatchServer
from .security import SecurityManager
from .chat import MatchChat

__all__ = [
    'GameClient',
    'MatchServer',
    'SecurityManager',
    'MatchChat',
]
