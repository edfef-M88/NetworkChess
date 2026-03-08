"""Управление уровнями сложности 1-100."""

class DifficultyManager:
    def normalize(self, level: int) -> int:
        return max(1, min(100, level))
