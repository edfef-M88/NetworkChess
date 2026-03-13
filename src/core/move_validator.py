"""Проверка корректности ходов."""

class MoveValidator:
    """Валидация шахматных ходов."""

    def __init__(self):
        self.board = None

    def set_board(self, board: list[list[str]]) -> None:
        """Установить текущую доску."""
        self.board = board

    def validate(self, from_cell: str, to_cell: str) -> bool:
        """Базовая проверка хода."""
        return bool(from_cell and to_cell and from_cell != to_cell)

    def validate_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int],
                     current_turn: str) -> tuple[bool, str]:
        """Полная валидация хода с объяснением."""
        if not self._is_valid_position(from_pos):
            return False, "Неверная начальная позиция"

        if not self._is_valid_position(to_pos):
            return False, "Неверная конечная позиция"

        piece = self.board[from_pos[0]][from_pos[1]]
        if piece == ".":
            return False, "На клетке нет фигуры"

        piece_color = "white" if piece.isupper() else "black"
        if piece_color != current_turn:
            return False, "Не ваша фигура"

        target = self.board[to_pos[0]][to_pos[1]]
        if target != ".":
            target_color = "white" if target.isupper() else "black"
            if target_color == piece_color:
                return False, "Нельзя взять свою фигуру"

        if not self._is_legal_piece_move(piece, from_pos, to_pos):
            return False, "Недопустимый ход для этой фигуры"

        return True, "Ход корректен"

    def _is_valid_position(self, pos: tuple[int, int]) -> bool:
        """Проверка, что позиция в пределах доски."""
        return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

    def _is_legal_piece_move(self, piece: str, from_pos: tuple[int, int],
                            to_pos: tuple[int, int]) -> bool:
        """Проверка хода для конкретной фигуры."""
        piece_type = piece.lower()
        if piece_type == "p":
            return self._validate_pawn_move(piece, from_pos, to_pos)
        elif piece_type == "n":
            return self._validate_knight_move(from_pos, to_pos)
        elif piece_type == "b":
            return self._validate_bishop_move(from_pos, to_pos)
        elif piece_type == "r":
            return self._validate_rook_move(from_pos, to_pos)
        elif piece_type == "q":
            return self._validate_queen_move(from_pos, to_pos)
        elif piece_type == "k":
            return self._validate_king_move(from_pos, to_pos)
        return False

    def _validate_pawn_move(self, piece: str, from_pos: tuple[int, int],
                           to_pos: tuple[int, int]) -> bool:
        """Валидация хода пешки."""
        direction = -1 if piece.isupper() else 1
        row_diff = to_pos[0] - from_pos[0]
        col_diff = abs(to_pos[1] - from_pos[1])

        if col_diff == 0 and row_diff == direction:
            return self.board[to_pos[0]][to_pos[1]] == "."
        elif col_diff == 1 and row_diff == direction:
            return self.board[to_pos[0]][to_pos[1]] != "."
        return False

    def _validate_knight_move(self, from_pos: tuple[int, int],
                             to_pos: tuple[int, int]) -> bool:
        """Валидация хода коня."""
        row_diff = abs(to_pos[0] - from_pos[0])
        col_diff = abs(to_pos[1] - from_pos[1])
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def _validate_bishop_move(self, from_pos: tuple[int, int],
                             to_pos: tuple[int, int]) -> bool:
        """Валидация хода слона."""
        return self._is_diagonal_move(from_pos, to_pos) and self._is_path_clear(from_pos, to_pos)

    def _validate_rook_move(self, from_pos: tuple[int, int],
                           to_pos: tuple[int, int]) -> bool:
        """Валидация хода ладьи."""
        return self._is_straight_move(from_pos, to_pos) and self._is_path_clear(from_pos, to_pos)

    def _validate_queen_move(self, from_pos: tuple[int, int],
                            to_pos: tuple[int, int]) -> bool:
        """Валидация хода ферзя."""
        return (self._is_diagonal_move(from_pos, to_pos) or
                self._is_straight_move(from_pos, to_pos)) and self._is_path_clear(from_pos, to_pos)

    def _validate_king_move(self, from_pos: tuple[int, int],
                           to_pos: tuple[int, int]) -> bool:
        """Валидация хода короля."""
        row_diff = abs(to_pos[0] - from_pos[0])
        col_diff = abs(to_pos[1] - from_pos[1])
        return row_diff <= 1 and col_diff <= 1

    def _is_diagonal_move(self, from_pos: tuple[int, int],
                         to_pos: tuple[int, int]) -> bool:
        """Проверка диагонального хода."""
        return abs(to_pos[0] - from_pos[0]) == abs(to_pos[1] - from_pos[1])

    def _is_straight_move(self, from_pos: tuple[int, int],
                         to_pos: tuple[int, int]) -> bool:
        """Проверка прямого хода."""
        return from_pos[0] == to_pos[0] or from_pos[1] == to_pos[1]

    def _is_path_clear(self, from_pos: tuple[int, int],
                      to_pos: tuple[int, int]) -> bool:
        """Проверка, что путь свободен."""
        row_step = 0 if from_pos[0] == to_pos[0] else (1 if to_pos[0] > from_pos[0] else -1)
        col_step = 0 if from_pos[1] == to_pos[1] else (1 if to_pos[1] > from_pos[1] else -1)

        current_row = from_pos[0] + row_step
        current_col = from_pos[1] + col_step

        while (current_row, current_col) != to_pos:
            if self.board[current_row][current_col] != ".":
                return False
            current_row += row_step
            current_col += col_step

        return True
