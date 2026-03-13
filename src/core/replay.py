"""Запись и воспроизведение партии."""

import json
from datetime import datetime

class ReplayManager:
    """Управление записью и воспроизведением партий."""

    def __init__(self) -> None:
        self.moves: list[str] = []
        self.timestamps: list[float] = []
        self.current_position = 0
        self.metadata = {
            "white_player": "",
            "black_player": "",
            "date": "",
            "result": "",
            "time_control": ""
        }

    def record_move(self, move: str, timestamp: float = None) -> None:
        """Записать ход."""
        self.moves.append(move)
        if timestamp is None:
            timestamp = datetime.now().timestamp()
        self.timestamps.append(timestamp)

    def set_metadata(self, white: str, black: str, time_control: str) -> None:
        """Установить метаданные партии."""
        self.metadata["white_player"] = white
        self.metadata["black_player"] = black
        self.metadata["date"] = datetime.now().isoformat()
        self.metadata["time_control"] = time_control

    def set_result(self, result: str) -> None:
        """Установить результат партии."""
        self.metadata["result"] = result

    def play_forward(self) -> str | None:
        """Воспроизвести следующий ход."""
        if self.current_position < len(self.moves):
            move = self.moves[self.current_position]
            self.current_position += 1
            return move
        return None

    def play_backward(self) -> str | None:
        """Вернуться на ход назад."""
        if self.current_position > 0:
            self.current_position -= 1
            return self.moves[self.current_position]
        return None

    def jump_to_move(self, move_number: int) -> bool:
        """Перейти к конкретному ходу."""
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
        """Получить ход на определенной позиции."""
        if 0 <= position < len(self.moves):
            return self.moves[position]
        return None

    def get_time_spent(self, move_number: int) -> float:
        """Получить время, затраченное на ход."""
        if 0 < move_number < len(self.timestamps):
            return self.timestamps[move_number] - self.timestamps[move_number - 1]
        return 0.0

    def export_pgn(self) -> str:
        """Экспортировать партию в формат PGN."""
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
        """Сохранить партию в файл."""
        data = {
            "metadata": self.metadata,
            "moves": self.moves,
            "timestamps": self.timestamps
        }
        try:
            with open(filename, "w") as f:
                json.dump(data, f, indent=2)
            return True
        except Exception:
            return False

    def load_from_file(self, filename: str) -> bool:
        """Загрузить партию из файла."""
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
