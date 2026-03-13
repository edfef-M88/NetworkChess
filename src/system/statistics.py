"""Статистика и история сыгранных партий.

Модуль содержит сервис :class:`StatisticsService`, который накапливает историю
партий и вычисляет простые метрики по игрокам:

- общий баланс побед/поражений/ничьих;
- серии побед;
- статистику по цветам (белыми/чёрными);
- статистику по дебютам и контролю времени;
- активность игрока за период и «тепловую карту» по дням недели;
- статистику по конкретным оппонентам.

В учебной реализации данные хранятся в памяти (в списках/словарях). Сохранение
на диск может выполняться отдельным модулем хранилища.

Classes:
    StatisticsService: Сбор статистики и вычисление отчётов по истории партий.
"""

from datetime import datetime, timedelta
from typing import Dict, List


class StatisticsService:
    """Сервис для сбора и анализа статистики игроков.

    Сервис получает на вход данные завершённых партий (в виде словаря) и
    преобразует их в унифицированную запись истории. Затем обновляет агрегированную
    статистику по каждому игроку.

    Attributes:
        games_history: Список записей партий (каждая запись — dict с полями
            game_id, white_player, black_player, result и др.).
        player_stats: Словарь агрегированной статистики игрока (имя → dict).
    """

    def __init__(self) -> None:
        """Создать сервис статистики с пустыми структурами.

        Returns:
            None
        """
        self.games_history: List[dict] = []
        self.player_stats: Dict[str, dict] = {}

    def record_game(self, game_data: dict) -> None:
        """Записать завершённую игру в историю и обновить статистику игроков.

        Args:
            game_data: Словарь данных партии. Ожидаемые ключи (необязательные):
                id, white, black, result, moves_count, duration, time_control,
                opening.

        Returns:
            None
        """
        game_record = {
            "game_id": game_data.get("id"),
            "white_player": game_data.get("white"),
            "black_player": game_data.get("black"),
            "result": game_data.get("result"),
            "moves_count": game_data.get("moves_count", 0),
            "duration": game_data.get("duration", 0),
            "timestamp": datetime.now().isoformat(),
            "time_control": game_data.get("time_control", ""),
            "opening": game_data.get("opening", "Unknown"),
        }
        self.games_history.append(game_record)
        self._update_player_stats(game_record)

    def summary(self, wins: int, losses: int, draws: int) -> dict:
        """Сформировать краткую сводку по W/L/D и winrate.

        Args:
            wins: Количество побед.
            losses: Количество поражений.
            draws: Количество ничьих.

        Returns:
            dict: Словарь сводки (wins, losses, draws, total, win_rate).
        """
        total = wins + losses + draws
        win_rate = (wins / total * 100) if total > 0 else 0
        return {
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "total": total,
            "win_rate": round(win_rate, 2),
        }

    def get_player_stats(self, player_name: str) -> dict:
        """Получить агрегированную статистику игрока.

        Args:
            player_name: Имя игрока.

        Returns:
            dict: Словарь статистики. Если игрок неизвестен — возвращается
            «пустая» структура с нулевыми значениями.
        """
        if player_name not in self.player_stats:
            return self._empty_stats()
        return self.player_stats[player_name]

    def get_recent_games(self, player_name: str, limit: int = 10) -> List[dict]:
        """Получить последние партии, в которых участвовал игрок.

        Args:
            player_name: Имя игрока.
            limit: Максимальное число возвращаемых записей.

        Returns:
            List[dict]: Список записей партий (не более limit).
        """
        player_games = [
            game
            for game in self.games_history
            if game["white_player"] == player_name or game["black_player"] == player_name
        ]
        return player_games[-limit:]

    def get_win_streak(self, player_name: str) -> int:
        """Получить текущую серию побед игрока.

        Сервис идёт от самых последних партий к более ранним и считает число
        подряд идущих побед.

        Args:
            player_name: Имя игрока.

        Returns:
            int: Длина серии побед (0, если текущая партия не победа или игр нет).
        """
        recent_games = self.get_recent_games(player_name, 100)
        streak = 0
        for game in reversed(recent_games):
            if self._is_win(game, player_name):
                streak += 1
            else:
                break
        return streak

    def get_performance_by_color(self, player_name: str) -> dict:
        """Получить статистику игрока отдельно для белых и чёрных.

        Args:
            player_name: Имя игрока.

        Returns:
            dict: Словарь с ключами "white" и "black", значения — summary().
        """
        white_stats = {"wins": 0, "losses": 0, "draws": 0}
        black_stats = {"wins": 0, "losses": 0, "draws": 0}

        for game in self.games_history:
            if game["white_player"] == player_name:
                self._update_color_stats(white_stats, game["result"], "white")
            elif game["black_player"] == player_name:
                self._update_color_stats(black_stats, game["result"], "black")

        return {
            "white": self.summary(white_stats["wins"], white_stats["losses"], white_stats["draws"]),
            "black": self.summary(black_stats["wins"], black_stats["losses"], black_stats["draws"]),
        }

    def get_opening_stats(self, player_name: str) -> Dict[str, dict]:
        """Получить статистику игрока по дебютам.

        Args:
            player_name: Имя игрока.

        Returns:
            Dict[str, dict]: Словарь (дебют → {wins, losses, draws, games}).
        """
        opening_stats: Dict[str, dict] = {}
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
        """Получить статистику игрока по контролям времени.

        Args:
            player_name: Имя игрока.

        Returns:
            Dict[str, dict]: Словарь (time_control → {wins, losses, draws}).
        """
        time_stats: Dict[str, dict] = {}
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
        """Вычислить среднюю длину партии игрока (в полуходах/ходах из записи).

        Args:
            player_name: Имя игрока.

        Returns:
            float: Среднее количество ходов (0.0, если игр нет).
        """
        player_games = [
            game
            for game in self.games_history
            if game["white_player"] == player_name or game["black_player"] == player_name
        ]
        if not player_games:
            return 0.0

        total_moves = sum(game["moves_count"] for game in player_games)
        return total_moves / len(player_games)

    def get_peak_rating(self, player_name: str) -> int:
        """Получить пиковый рейтинг игрока (если хранится в агрегатах).

        Args:
            player_name: Имя игрока.

        Returns:
            int: Пиковое значение рейтинга либо значение по умолчанию (1200).
        """
        if player_name in self.player_stats:
            return self.player_stats[player_name].get("peak_rating", 1200)
        return 1200

    def get_games_by_period(self, player_name: str, days: int = 7) -> List[dict]:
        """Получить список партий игрока за последние N дней.

        Args:
            player_name: Имя игрока.
            days: Глубина окна в днях.

        Returns:
            List[dict]: Список записей партий, попадающих в период.
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            game
            for game in self.games_history
            if (game["white_player"] == player_name or game["black_player"] == player_name)
            and datetime.fromisoformat(game["timestamp"]) > cutoff_date
        ]

    def get_activity_heatmap(self, player_name: str) -> Dict[str, int]:
        """Построить «тепловую карту» активности по дням недели.

        Ключи словаря — номера дней недели ("0".."6"), где 0 = понедельник
        (как в datetime.weekday()).

        Args:
            player_name: Имя игрока.

        Returns:
            Dict[str, int]: Количество партий по дням недели.
        """
        heatmap = {str(i): 0 for i in range(7)}
        for game in self.games_history:
            if game["white_player"] == player_name or game["black_player"] == player_name:
                timestamp = datetime.fromisoformat(game["timestamp"])
                day_of_week = str(timestamp.weekday())
                heatmap[day_of_week] += 1
        return heatmap

    def get_opponent_stats(self, player_name: str) -> Dict[str, dict]:
        """Получить статистику игрока против конкретных оппонентов.

        Args:
            player_name: Имя игрока.

        Returns:
            Dict[str, dict]: Словарь (имя оппонента → {wins, losses, draws}).
        """
        opponent_stats: Dict[str, dict] = {}
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
        """Обновить агрегированную статистику по игрокам на основе партии.

        Args:
            game: Унифицированная запись партии из games_history.

        Returns:
            None
        """
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
        """Проверить, является ли партия победой для указанного игрока.

        Args:
            game: Запись партии.
            player_name: Имя игрока.

        Returns:
            bool: True, если результат партии соответствует победе игрока.
        """
        result = game["result"]
        if game["white_player"] == player_name:
            return result == "1-0"
        elif game["black_player"] == player_name:
            return result == "0-1"
        return False

    def _is_loss(self, game: dict, player_name: str) -> bool:
        """Проверить, является ли партия поражением для указанного игрока.

        Args:
            game: Запись партии.
            player_name: Имя игрока.

        Returns:
            bool: True, если результат партии соответствует поражению игрока.
        """
        result = game["result"]
        if game["white_player"] == player_name:
            return result == "0-1"
        elif game["black_player"] == player_name:
            return result == "1-0"
        return False

    def _update_color_stats(self, stats: dict, result: str, color: str) -> None:
        """Обновить счётчики побед/поражений/ничьих для игры данным цветом.

        Args:
            stats: Словарь-счётчик с ключами wins/losses/draws.
            result: Результат партии ("1-0", "0-1", "1/2-1/2").
            color: Цвет игрока в данной партии ("white" или "black").

        Returns:
            None
        """
        if (color == "white" and result == "1-0") or (color == "black" and result == "0-1"):
            stats["wins"] += 1
        elif (color == "white" and result == "0-1") or (color == "black" and result == "1-0"):
            stats["losses"] += 1
        else:
            stats["draws"] += 1

    def _empty_stats(self) -> dict:
        """Создать «пустую» структуру статистики для нового игрока.

        Returns:
            dict: Структура с нулевыми счётчиками и дефолтными значениями.
        """
        return {
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "peak_rating": 1200,
        }
