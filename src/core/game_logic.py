"""Базовая игровая логика шахматной партии."""

class GameLogic:
    def is_checkmate(self, legal_moves: int, king_in_check: bool) -> bool:
        return legal_moves == 0 and king_in_check
