"""Запись и воспроизведение партий.

Модуль реализует менеджер повторов (replay): хранение последовательности
ходов, временных меток, базовых метаданных партии, экспорт в PGN, а также
сохранение/загрузка в JSON.

Classes:
    ReplayManager: Запись ходов и навигация по истории.
"""

import json
from datetime import datetime


class ReplayManager:
    """Управление записью и воспроизведением партий.

    Attributes:
        moves: Список ходов в строковом виде.
        timestamps: Список временных меток для каждого хода.
        current_position: Текущая позиция «курсор» воспроизведения (индекс хода).
        metadata: Метаданные партии (игроки, дата, результат, контроль времени).
    """

    def __init__(self) -> None:
        """Создать новый менеджер повторов с пустой историей."""
        self.moves: list[str] = []
        self.timestamps: list[float] = []
        self.current_position = 0
        self.metadata = {
            "white_player": "",
            "black_player": "",
            "date": "",
            "result": "",
            "time_control": "",
        }

    def record_move(self, move: str, timestamp: float = None) -> None:
        """Записать ход (и время выполнения хода).

        Args:
            move: Ход в строковой нотации.
            timestamp: UNIX timestamp (секунды). Если не задан, берётся текущее время.

        Returns:
            None
        """
        self.moves.append(move)
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        self.timestamps.append(timestamp)

    def set_metadata(self, white: str, black: str, time_control: str) -> None:
        """Установить метаданные партии.

        Args:
            white: Имя игрока белыми.
            black: Имя игрока чёрными.
            time_control: Контроль времени (например, "10+0").

        Returns:
            None
        """
        self.metadata["white_player"] = white
        self.metadata["black_player"] = black
        self.metadata["date"] = datetime.now().isoformat()
        self.metadata["time_control"] = time_control

    def set_result(self, result: str) -> None:
        """Установить результат партии.

        Args:
            result: Строка результата ("1-0", "0-1", "1/2-1/2").

        Returns:
            None
        """
        self.metadata["result"] = result

    def play_forward(self) -> str | None:
        """Переместиться вперёд на один ход и вернуть его.

        Returns:
            str | None: Следующий ход либо None, если достигнут конец.
        """
        if self.current_position < len(self.moves):
            move = self.moves[self.current_position]
            self.current_position += 1
            return move
        return None

    def play_backward(self) -> str | None:
        """Переместиться назад на один ход и вернуть ход в новой позиции.

        Returns:
            str | None: Ход на новой позиции, либо None, если уже в начале.
        """
        if self.current_position > 0:
            self.current_position -= 1
            return self.moves[self.current_position]
        return None

    def jump_to_move(self, move_number: int) -> bool:
        """Перейти к конкретному номеру хода.

        Args:
            move_number: Индекс позиции (0..len(moves)).

        Returns:
            bool: True при успешном переходе.
        """
        if 0 <= move_number <= len(self.moves):
            self.current_position = move_number
            return True
        return False

    def jump_to_start(self) -> None:
        """Перейти к началу партии."""
        self.current_position = 0

    def jump_to_end(self) -> None:
        """Перейти к концу партии."""
        self.current_position = len(self.moves)

    def get_move_at(self, position: int) -> str | None:
        """Получить ход по индексу без изменения текущей позиции.

        Args:
            position: Индекс хода.

        Returns:
            str | None: Ход или None.
        """
        if 0 <= position < len(self.moves):
            return self.moves[position]
        return None

    def get_time_spent(self, move_number: int) -> float:
        """Получить время, затраченное на конкретный ход.

        Args:
            move_number: Номер хода.

        Returns:
            float: Разница временных меток (в секундах).
        """
        if 0 < move_number < len(self.timestamps):
            return self.timestamps[move_number] - self.timestamps[move_number - 1]
        return 0.0

    def export_pgn(self) -> str:
        """Экспортировать партию в формат PGN.

        Returns:
            str: Строка PGN.
        """
        pgn = f'[White "{self.metadata["white_player"]}"]\n'
        pgn += f'[Black "{self.metadata["black_player"]}"]\n'
        pgn += f'[Date "{self.metadata["date"]}"]\n'
        pgn += f'[Result "{self.metadata["result"]}"]\n\n'

        for i, move in enumerate(self.moves):
            if i % 2 == 0:
                pgn += f"{i//2 + 1}. "
            pgn += f"{move} "

        pgn += self.metadata["result"]
        return pgn

    def save_to_file(self, filename: str) -> bool:
        """Сохранить данные повтора в JSON файл.

        Args:
            filename: Путь к файлу.

        Returns:
            bool: True при успешном сохранении.
        """
        data = {"metadata": self.metadata, "moves": self.moves, "timestamps": self.timestamps}
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def load_from_file(self, filename: str) -> bool:
        """Загрузить повтор из JSON файла.

        Args:
            filename: Путь к файлу.

        Returns:
            bool: True при успешной загрузке.
        """
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            self.metadata = data["metadata"]
            self.moves = data["moves"]
            self.timestamps = data["timestamps"]
            self.current_position = 0
            return True
        except Exception:
            return False
