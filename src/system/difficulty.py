"""Управление уровнями сложности ИИ (1–100).

Модуль содержит класс :class:`DifficultyManager`, который инкапсулирует логику
работы с «уровнем сложности» в диапазоне 1..100.

В рамках учебного проекта NetworkChess уровень сложности используется как единая
шкала, из которой выводятся параметры поведения ИИ:

- глубина поиска (search_depth);
- целевое время «обдумывания» (think_time);
- вероятность «ошибки» (error_rate);
- включение/отключение дополнительных эвристик (opening_book/endgame_tables).

Важно: менеджер сложности сам по себе не реализует шахматный движок. Он лишь
преобразует числовой уровень в набор параметров, которые затем используются в
модуле ИИ (например, в :class:`src.system.ai_engine.AIEngine`).

Classes:
    DifficultyManager: Хранит и нормализует уровень сложности, предоставляет
        пресеты, описания и вспомогательные расчёты.
"""

from typing import Dict


class DifficultyManager:
    """Управление уровнем сложности ИИ и преобразование его в параметры.

    Класс хранит текущий уровень сложности (1..100), предоставляет операции
    изменения уровня, работу с именованными пресетами, а также методы, которые
    помогают UI/логике игры отображать понятное описание уровня.

    Attributes:
        current_level: Текущий уровень сложности (1..100).
        min_level: Нижняя граница шкалы (в проекте — 1).
        max_level: Верхняя граница шкалы (в проекте — 100).
        presets: Словарь пресетов, где ключ — имя ("easy"/"hard" и т.п.),
            значение — числовой уровень.
    """

    def __init__(self) -> None:
        """Создать менеджер сложности со значениями по умолчанию.

        По умолчанию текущий уровень устанавливается в 50 (условно «средний»).

        Returns:
            None
        """
        self.current_level = 50
        self.min_level = 1
        self.max_level = 100
        self.presets = self._init_presets()

    def _init_presets(self) -> Dict[str, int]:
        """Инициализировать таблицу предустановок сложности.

        Returns:
            Dict[str, int]: Словарь пресетов (имя → уровень 1..100).
        """
        return {
            "beginner": 20,
            "easy": 35,
            "medium": 50,
            "hard": 70,
            "expert": 85,
            "master": 95,
        }

    def normalize(self, level: int) -> int:
        """Нормализовать уровень, приведя его к диапазону 1..100.

        Args:
            level: Произвольное целое число уровня.

        Returns:
            int: Значение, ограниченное диапазоном [min_level, max_level].
        """
        return max(self.min_level, min(self.max_level, level))

    def set_level(self, level: int) -> bool:
        """Установить уровень сложности без «автокоррекции».

        Метод пытается применить указанный уровень. Если значение выходит за
        пределы шкалы (1..100), возвращается False, а состояние не меняется.

        Args:
            level: Требуемый уровень сложности.

        Returns:
            bool: True, если уровень был принят и применён. False, если уровень
            был вне допустимого диапазона.
        """
        normalized = self.normalize(level)
        if normalized != level:
            return False
        self.current_level = normalized
        return True

    def get_level(self) -> int:
        """Получить текущий уровень сложности.

        Returns:
            int: Текущий уровень 1..100.
        """
        return self.current_level

    def increase_level(self, amount: int = 5) -> int:
        """Увеличить уровень сложности на указанную величину.

        Args:
            amount: Прибавка к уровню (может быть отрицательной, но это не
                основное назначение метода).

        Returns:
            int: Новый уровень после нормализации.
        """
        new_level = self.normalize(self.current_level + amount)
        self.current_level = new_level
        return new_level

    def decrease_level(self, amount: int = 5) -> int:
        """Уменьшить уровень сложности на указанную величину.

        Args:
            amount: Величина уменьшения уровня.

        Returns:
            int: Новый уровень после нормализации.
        """
        new_level = self.normalize(self.current_level - amount)
        self.current_level = new_level
        return new_level

    def set_preset(self, preset_name: str) -> bool:
        """Установить уровень по имени предустановки.

        Args:
            preset_name: Имя пресета (например, "easy", "hard").

        Returns:
            bool: True, если пресет найден и применён. False, если такого пресета
            нет в таблице.
        """
        if preset_name in self.presets:
            self.current_level = self.presets[preset_name]
            return True
        return False

    def get_preset_name(self, level: int | None = None) -> str:
        """Получить имя пресета, соответствующее уровню.

        Метод использует диапазоны уровней и возвращает имя «ближайшей категории».

        Args:
            level: Уровень, для которого нужно определить категорию. Если None,
                используется текущий уровень.

        Returns:
            str: Имя категории ("beginner"/"easy"/"medium"/"hard"/"expert"/"master").
        """
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

    def get_description(self, level: int | None = None) -> str:
        """Получить человекочитаемое описание уровня сложности.

        Args:
            level: Уровень сложности для описания. Если None, берётся текущий.

        Returns:
            str: Текстовое описание уровня.
        """
        if level is None:
            level = self.current_level

        descriptions = {
            "beginner": "Для начинающих игроков. AI делает случайные ходы.",
            "easy": "Легкий уровень. AI делает простые тактические ходы.",
            "medium": "Средний уровень. AI планирует на 2-3 хода вперед.",
            "hard": "Сложный уровень. AI использует продвинутую тактику.",
            "expert": "Экспертный уровень. AI анализирует глубокие варианты.",
            "master": "Мастерский уровень. AI играет на уровне сильного игрока.",
        }

        preset = self.get_preset_name(level)
        return descriptions.get(preset, "Неизвестный уровень")

    def get_ai_parameters(self, level: int | None = None) -> dict:
        """Получить набор параметров ИИ, выведенный из уровня сложности.

        Возвращаемая структура предназначена для передачи в AI-слой и/или
        отображения в UI. Значения являются учебными и не претендуют на точную
        модель реального шахматного движка.

        Args:
            level: Уровень сложности. Если None, берётся текущий.

        Returns:
            dict: Словарь параметров ИИ. Ожидаемые ключи:

            - search_depth (int): глубина поиска;
            - think_time (int): целевое время на ход в миллисекундах;
            - error_rate (int): вероятность ошибки в процентах;
            - use_opening_book (bool): использовать ли «книгу дебютов»;
            - use_endgame_tables (bool): использовать ли «эндшпильные таблицы»;
            - contempt_factor (float): условный коэффициент «нежелания ничьей».
        """
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
            "contempt_factor": level / 100.0,
        }

    def calculate_rating_equivalent(self, level: int | None = None) -> int:
        """Рассчитать «эквивалентный» рейтинг Elo для заданного уровня.

        Это вспомогательная (примерная) функция, полезная для интерфейса и отчётов:
        она показывает, как выбранный уровень может соотноситься с рейтингом.

        Args:
            level: Уровень сложности. Если None, берётся текущий.

        Returns:
            int: Приблизительный рейтинг.
        """
        if level is None:
            level = self.current_level

        # Примерная формула перевода уровня в рейтинг
        base_rating = 800
        rating_per_level = 20
        return base_rating + (level * rating_per_level)

    def suggest_level_for_rating(self, player_rating: int) -> int:
        """Предложить уровень сложности, исходя из рейтинга игрока.

        Args:
            player_rating: Рейтинг игрока (условный Elo).

        Returns:
            int: Предлагаемый уровень в диапазоне 1..100.
        """
        # Обратная формула
        suggested = (player_rating - 800) // 20
        return self.normalize(suggested)

    def adaptive_adjust(self, game_result: str, moves_count: int) -> int:
        """Адаптивно скорректировать сложность по результату партии.

        Метод реализует упрощённую идею: после партии сложность может изменяться
        в зависимости от исхода (win/loss/другое) и длины партии.

        Args:
            game_result: Результат относительно игрока ("win"/"loss"/"draw" или
                любое другое значение).
            moves_count: Количество ходов в партии (используется для оценки
                «быстроты» победы/поражения).

        Returns:
            int: Новый текущий уровень сложности после корректировки.
        """
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
        """Получить все пресеты вместе с описаниями и рейтингом.

        Returns:
            Dict[str, dict]: Словарь вида:

                {
                    "easy": {"level": 35, "description": "...", "rating": 1500},
                    ...
                }
        """
        return {
            name: {
                "level": level,
                "description": self.get_description(level),
                "rating": self.calculate_rating_equivalent(level),
            }
            for name, level in self.presets.items()
        }

    def reset_to_default(self) -> None:
        """Сбросить уровень сложности к значению по умолчанию.

        Returns:
            None
        """
        self.current_level = 50
