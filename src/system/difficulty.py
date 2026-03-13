"""Управление уровнями сложности 1-100."""

from typing import Dict

class DifficultyManager:
    """Управление уровнями сложности AI."""

    def __init__(self):
        self.current_level = 50
        self.min_level = 1
        self.max_level = 100
        self.presets = self._init_presets()

    def _init_presets(self) -> Dict[str, int]:
        """Инициализировать предустановки сложности."""
        return {
            "beginner": 20,
            "easy": 35,
            "medium": 50,
            "hard": 70,
            "expert": 85,
            "master": 95
        }

    def normalize(self, level: int) -> int:
        """Нормализовать уровень в диапазон 1-100."""
        return max(self.min_level, min(self.max_level, level))

    def set_level(self, level: int) -> bool:
        """Установить уровень сложности."""
        normalized = self.normalize(level)
        if normalized != level:
            return False
        self.current_level = normalized
        return True

    def get_level(self) -> int:
        """Получить текущий уровень."""
        return self.current_level

    def increase_level(self, amount: int = 5) -> int:
        """Увеличить уровень сложности."""
        new_level = self.normalize(self.current_level + amount)
        self.current_level = new_level
        return new_level

    def decrease_level(self, amount: int = 5) -> int:
        """Уменьшить уровень сложности."""
        new_level = self.normalize(self.current_level - amount)
        self.current_level = new_level
        return new_level

    def set_preset(self, preset_name: str) -> bool:
        """Установить предустановленный уровень."""
        if preset_name in self.presets:
            self.current_level = self.presets[preset_name]
            return True
        return False

    def get_preset_name(self, level: int = None) -> str:
        """Получить название предустановки для уровня."""
        if level is None:
            level = self.current_level

        if level <= 25:
            return "beginner"
        elif level <= 40:
            return "easy"
        elif level <= 60:
            return "medium"
        elif level <= 75:
            return "hard"
        elif level <= 90:
            return "expert"
        else:
            return "master"

    def get_description(self, level: int = None) -> str:
        """Получить описание уровня сложности."""
        if level is None:
            level = self.current_level

        descriptions = {
            "beginner": "Для начинающих игроков. AI делает случайные ходы.",
            "easy": "Легкий уровень. AI делает простые тактические ходы.",
            "medium": "Средний уровень. AI планирует на 2-3 хода вперед.",
            "hard": "Сложный уровень. AI использует продвинутую тактику.",
            "expert": "Экспертный уровень. AI анализирует глубокие варианты.",
            "master": "Мастерский уровень. AI играет на уровне сильного игрока."
        }

        preset = self.get_preset_name(level)
        return descriptions.get(preset, "Неизвестный уровень")

    def get_ai_parameters(self, level: int = None) -> dict:
        """Получить параметры AI для уровня."""
        if level is None:
            level = self.current_level

        # Глубина поиска
        if level <= 30:
            search_depth = 1
        elif level <= 60:
            search_depth = 2
        elif level <= 85:
            search_depth = 3
        else:
            search_depth = 4

        # Время на ход (мс)
        if level <= 40:
            think_time = 500
        elif level <= 70:
            think_time = 1000
        else:
            think_time = 2000

        # Вероятность ошибки (%)
        if level <= 20:
            error_rate = 30
        elif level <= 50:
            error_rate = 15
        elif level <= 80:
            error_rate = 5
        else:
            error_rate = 1

        return {
            "search_depth": search_depth,
            "think_time": think_time,
            "error_rate": error_rate,
            "use_opening_book": level >= 40,
            "use_endgame_tables": level >= 70,
            "contempt_factor": level / 100.0
        }

    def calculate_rating_equivalent(self, level: int = None) -> int:
        """Рассчитать эквивалентный рейтинг Elo."""
        if level is None:
            level = self.current_level

        # Примерная формула перевода уровня в рейтинг
        base_rating = 800
        rating_per_level = 20
        return base_rating + (level * rating_per_level)

    def suggest_level_for_rating(self, player_rating: int) -> int:
        """Предложить уровень для рейтинга игрока."""
        # Обратная формула
        suggested = (player_rating - 800) // 20
        return self.normalize(suggested)

    def adaptive_adjust(self, game_result: str, moves_count: int) -> int:
        """Адаптивная настройка сложности по результату игры."""
        if game_result == "win":
            # Игрок выиграл - увеличить сложность
            if moves_count < 20:
                # Быстрая победа - значительно увеличить
                adjustment = 10
            else:
                adjustment = 5
            return self.increase_level(adjustment)
        elif game_result == "loss":
            # Игрок проиграл - уменьшить сложность
            if moves_count < 20:
                # Быстрое поражение - значительно уменьшить
                adjustment = 10
            else:
                adjustment = 5
            return self.decrease_level(adjustment)
        else:
            # Ничья - небольшая корректировка
            return self.increase_level(2)

    def get_all_presets(self) -> Dict[str, dict]:
        """Получить все предустановки с описаниями."""
        return {
            name: {
                "level": level,
                "description": self.get_description(level),
                "rating": self.calculate_rating_equivalent(level)
            }
            for name, level in self.presets.items()
        }

    def reset_to_default(self) -> None:
        """Сбросить на уровень по умолчанию."""
        self.current_level = 50
