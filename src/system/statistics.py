"""Статистика и история партий."""

class StatisticsService:
    def summary(self, wins: int, losses: int, draws: int) -> dict:
        return {"wins": wins, "losses": losses, "draws": draws}
