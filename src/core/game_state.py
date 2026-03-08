"""Хранение текущего состояния партии."""

class GameState:
    def __init__(self) -> None:
        self.current_turn = "white"
        self.move_history: list[str] = []
