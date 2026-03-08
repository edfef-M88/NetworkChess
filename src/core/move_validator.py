"""Проверка корректности ходов."""

class MoveValidator:
    def validate(self, from_cell: str, to_cell: str) -> bool:
        return bool(from_cell and to_cell and from_cell != to_cell)
