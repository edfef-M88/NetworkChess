"""Отображение шахматной доски и фигур."""

class BoardRenderer:
    def render(self, board_state: list[list[str]]) -> None:
        for row in board_state:
            print(" ".join(row))
