"""Статистика и история партий."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

class StatisticsService:
    """Сервис для сбора и анализа статистики."""

    def __init__(self):
        self.games_history: List[dict] = []
        self.player_stats: Dict[str, dict] = {}

    def record_game(self, game_data: dict) -> None:
        """Записать завершенную игру."""
        game_record = {
            "game_id": game_data.get("id"),
            "white_player": game_data.get("white"),
            "black_player": game_data.get("black"),
            "result": game_data.get("result"),
            "moves_count": game_data.get("moves_count", 0),
            "duration": game_data.get("duration", 0),
            "timestamp": datetime.now().isoformat(),
            "time_control": game_data.get("time_control", ""),
            "opening": game_data.get("opening", "Unknown")
        }
        self.games_history.append(game_record)
        self._update_player_stats(game_record)

    def summary(self, wins: int, losses: int, draws: int) -> dict:
        """Получить краткую сводку."""
        total = wins + losses + draws
        win_rate = (wins / total * 100) if total > 0 else 0
        return {
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "total": total,
            "win_rate": round(win_rate, 2)
        }

    def get_player_stats(self, player_name: str) -> dict:
        """Получить статистику игрока."""
        if player_name not in self.player_stats:
            return self._empty_stats()
        return self.player_stats[player_name]

    def get_recent_games(self, player_name: str, limit: int = 10) -> List[dict]:
        """Получить последние игры игрока."""
        player_games = [
            game for game in self.games_history
            if game["white_player"] == player_name or game["black_player"] == player_name
        ]
        return player_games[-limit:]

    def get_win_streak(self, player_name: str) -> int:
        """Получить текущую серию побед."""
        recent_games = self.get_recent_games(player_name, 100)
        streak = 0
        for game in reversed(recent_games):
            if self._is_win(game, player_name):
                streak += 1
            else:
                break
        return streak

    def get_performance_by_color(self, player_name: str) -> dict:
        """Статистика по цветам."""
        white_stats = {"wins": 0, "losses": 0, "draws": 0}
        black_stats = {"wins": 0, "losses": 0, "draws": 0}

        for game in self.games_history:
            if game["white_player"] == player_name:
                self._update_color_stats(white_stats, game["result"], "white")
            elif game["black_player"] == player_name:
                self._update_color_stats(black_stats, game["result"], "black")

        return {
            "white": self.summary(white_stats["wins"], white_stats["losses"], white_stats["draws"]),
            "black": self.summary(black_stats["wins"], black_stats["losses"], black_stats["draws"])
        }

    def get_opening_stats(self, player_name: str) -> Dict[str, dict]:
        """Статистика по дебютам."""
        opening_stats = {}
        for game in self.games_history:
            if game["white_player"] == player_name or game["black_player"] == player_name:
                opening = game["opening"]
                if opening not in opening_stats:
                    opening_stats[opening] = {"wins": 0, "losses": 0, "draws": 0, "games": 0}

                opening_stats[opening]["games"] += 1
                if self._is_win(game, player_name):
                    opening_stats[opening]["wins"] += 1
                elif self._is_loss(game, player_name):
                    opening_stats[opening]["losses"] += 1
                else:
                    opening_stats[opening]["draws"] += 1

        return opening_stats

    def get_time_control_stats(self, player_name: str) -> Dict[str, dict]:
        """Статистика по контролю времени."""
        time_stats = {}
        for game in self.games_history:
            if game["white_player"] == player_name or game["black_player"] == player_name:
                tc = game["time_control"]
                if tc not in time_stats:
                    time_stats[tc] = {"wins": 0, "losses": 0, "draws": 0}

                if self._is_win(game, player_name):
                    time_stats[tc]["wins"] += 1
                elif self._is_loss(game, player_name):
                    time_stats[tc]["losses"] += 1
                else:
                    time_stats[tc]["draws"] += 1

        return time_stats

    def get_average_game_length(self, player_name: str) -> float:
        """Средняя длина игры в ходах."""
        player_games = [
            game for game in self.games_history
            if game["white_player"] == player_name or game["black_player"] == player_name
        ]
        if not player_games:
            return 0.0

        total_moves = sum(game["moves_count"] for game in player_games)
        return total_moves / len(player_games)

    def get_peak_rating(self, player_name: str) -> int:
        """Получить пиковый рейтинг."""
        if player_name in self.player_stats:
            return self.player_stats[player_name].get("peak_rating", 1200)
        return 1200

    def get_games_by_period(self, player_name: str, days: int = 7) -> List[dict]:
        """Получить игры за период."""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            game for game in self.games_history
            if (game["white_player"] == player_name or game["black_player"] == player_name)
            and datetime.fromisoformat(game["timestamp"]) > cutoff_date
        ]

    def get_activity_heatmap(self, player_name: str) -> Dict[str, int]:
        """Тепловая карта активности по дням недели."""
        heatmap = {str(i): 0 for i in range(7)}
        for game in self.games_history:
            if game["white_player"] == player_name or game["black_player"] == player_name:
                timestamp = datetime.fromisoformat(game["timestamp"])
                day_of_week = str(timestamp.weekday())
                heatmap[day_of_week] += 1
        return heatmap

    def get_opponent_stats(self, player_name: str) -> Dict[str, dict]:
        """Статистика против конкретных оппонентов."""
        opponent_stats = {}
        for game in self.games_history:
            opponent = None
            if game["white_player"] == player_name:
                opponent = game["black_player"]
            elif game["black_player"] == player_name:
                opponent = game["white_player"]

            if opponent:
                if opponent not in opponent_stats:
                    opponent_stats[opponent] = {"wins": 0, "losses": 0, "draws": 0}

                if self._is_win(game, player_name):
                    opponent_stats[opponent]["wins"] += 1
                elif self._is_loss(game, player_name):
                    opponent_stats[opponent]["losses"] += 1
                else:
                    opponent_stats[opponent]["draws"] += 1

        return opponent_stats

    def _update_player_stats(self, game: dict) -> None:
        """Обновить статистику игроков."""
        for player in [game["white_player"], game["black_player"]]:
            if player not in self.player_stats:
                self.player_stats[player] = self._empty_stats()

            stats = self.player_stats[player]
            stats["games_played"] += 1

            if self._is_win(game, player):
                stats["wins"] += 1
            elif self._is_loss(game, player):
                stats["losses"] += 1
            else:
                stats["draws"] += 1

    def _is_win(self, game: dict, player_name: str) -> bool:
        """Проверить, выиграл ли игрок."""
        result = game["result"]
        if game["white_player"] == player_name:
            return result == "1-0"
        elif game["black_player"] == player_name:
            return result == "0-1"
        return False

    def _is_loss(self, game: dict, player_name: str) -> bool:
        """Проверить, проиграл ли игрок."""
        result = game["result"]
        if game["white_player"] == player_name:
            return result == "0-1"
        elif game["black_player"] == player_name:
            return result == "1-0"
        return False

    def _update_color_stats(self, stats: dict, result: str, color: str) -> None:
        """Обновить статистику по цвету."""
        if (color == "white" and result == "1-0") or (color == "black" and result == "0-1"):
            stats["wins"] += 1
        elif (color == "white" and result == "0-1") or (color == "black" and result == "1-0"):
            stats["losses"] += 1
        else:
            stats["draws"] += 1

    def _empty_stats(self) -> dict:
        """Пустая статистика."""
        return {
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "peak_rating": 1200
        }
