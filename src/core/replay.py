"""Запись и воспроизведение партии."""

class ReplayManager:
    def __init__(self) -> None:
        self.moves: list[str] = []
