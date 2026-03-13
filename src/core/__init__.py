"""Ядро игры: логика, состояние и вспомогательные компоненты.

Пакет объединяет основные сущности, необходимые для ведения шахматной партии:
- :class:`~src.core.game_logic.GameLogic` — работа с доской и базовыми правилами;
- :class:`~src.core.game_state.GameState` — состояние партии (ход, история и т.п.);
- :class:`~src.core.move_validator.MoveValidator` — проверка корректности ходов;
- :class:`~src.core.replay.ReplayManager` — запись и воспроизведение партий.
"""

from .game_logic import GameLogic
from .game_state import GameState
from .move_validator import MoveValidator
from .replay import ReplayManager

__all__ = [
    'GameLogic',
    'GameState',
    'MoveValidator',
    'ReplayManager',
]
