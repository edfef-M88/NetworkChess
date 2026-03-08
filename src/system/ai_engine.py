"""Искусственный интеллект для режима игры против компьютера."""

class AIEngine:
    def choose_move(self, difficulty: int) -> str:
        return "e2e4" if difficulty < 50 else "d2d4"
