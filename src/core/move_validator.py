"""Проверка корректности шахматных ходов.

Модуль реализует базовую валидацию: проверка координат в пределах доски,
наличие фигуры на стартовой клетке, проверка очереди хода, запрет взятия
своих фигур, а также примитивная проверка «геометрии» хода для каждого типа
фигуры и свободного пути для скользящих фигур.

Classes:
    MoveValidator: Валидатор ходов по текущей доске.
"""


class MoveValidator:
    """Валидация шахматных ходов.

    Attributes:
        board: Текущая доска в виде матрицы 8×8 ("." — пустая клетка).
    """

    def __init__(self):
        """Создать валидатор (доска по умолчанию не установлена)."""
        self.board = None

    def set_board(self, board: list[list[str]]) -> None:
        """Установить текущую доску.

        Args:
            board: Матрица 8×8.

        Returns:
            None
        """
        self.board = board

    def validate(self, from_cell: str, to_cell: str) -> bool:
        """Выполнить минимальную проверку входных данных.

        Args:
            from_cell: Стартовая клетка (строка).
            to_cell: Конечная клетка (строка).

        Returns:
            bool: True, если строки заданы и клетки различаются.
        """
        return bool(from_cell and to_cell and from_cell != to_cell)

    def validate_move(
        self,
        from_pos: tuple[int, int],
        to_pos: tuple[int, int],
        current_turn: str,
    ) -> tuple[bool, str]:
        """Проверить корректность хода и вернуть объяснение.

        Args:
            from_pos: Начальная позиция (row, col).
            to_pos: Конечная позиция (row, col).
            current_turn: Цвет, который должен ходить ("white"/"black").

        Returns:
            tuple[bool, str]: (признак корректности, сообщение).

        Raises:
            TypeError: Может возникнуть, если board не установлена и обращение к ней невозможно.
        """
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
        """Проверить, что позиция находится в пределах доски.

        Args:
            pos: Координаты (row, col).

        Returns:
            bool: True, если 0..7 для строки и столбца.
        """
        return 0 <= pos[0] < 8 and 0 <= pos[1] < 8

    def _is_legal_piece_move(self, piece: str, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """Проверить допустимость хода для конкретного типа фигуры.

        Args:
            piece: Символ фигуры.
            from_pos: Начальная позиция.
            to_pos: Конечная позиция.

        Returns:
            bool: True, если ход соответствует правилам фигуры.
        """
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

    def _validate_pawn_move(self, piece: str, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """Проверить ход пешки (упрощённо).

        Args:
            piece: Символ пешки.
            from_pos: Начальная позиция.
            to_pos: Конечная позиция.

        Returns:
            bool: True, если ход соответствует базовой логике (1 шаг вперёд или взятие по диагонали).
        """
        direction = -1 if piece.isupper() else 1
        row_diff = to_pos[0] - from_pos[0]
        col_diff = abs(to_pos[1] - from_pos[1])

        if col_diff == 0 and row_diff == direction:
            return self.board[to_pos[0]][to_pos[1]] == "."
        elif col_diff == 1 and row_diff == direction:
            return self.board[to_pos[0]][to_pos[1]] != "."
        return False

    def _validate_knight_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """Проверить ход коня.

        Args:
            from_pos: Начальная позиция.
            to_pos: Конечная позиция.

        Returns:
            bool: True, если смещение соответствует (2,1) или (1,2).
        """
        row_diff = abs(to_pos[0] - from_pos[0])
        col_diff = abs(to_pos[1] - from_pos[1])
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)

    def _validate_bishop_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """Проверить ход слона.

        Returns:
            bool: True, если ход диагональный и путь свободен.
        """
        return self._is_diagonal_move(from_pos, to_pos) and self._is_path_clear(from_pos, to_pos)

    def _validate_rook_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """Проверить ход ладьи.

        Returns:
            bool: True, если ход прямой и путь свободен.
        """
        return self._is_straight_move(from_pos, to_pos) and self._is_path_clear(from_pos, to_pos)

    def _validate_queen_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """Проверить ход ферзя.

        Returns:
            bool: True, если ход прямой/диагональный и путь свободен.
        """
        return (
            (self._is_diagonal_move(from_pos, to_pos) or self._is_straight_move(from_pos, to_pos))
            and self._is_path_clear(from_pos, to_pos)
        )

    def _validate_king_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """Проверить ход короля (без рокировки).

        Returns:
            bool: True, если король перемещается не более чем на 1 клетку.
        """
        row_diff = abs(to_pos[0] - from_pos[0])
        col_diff = abs(to_pos[1] - from_pos[1])
        return row_diff <= 1 and col_diff <= 1

    def _is_diagonal_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """Проверить, что ход является диагональным."""
        return abs(to_pos[0] - from_pos[0]) == abs(to_pos[1] - from_pos[1])

    def _is_straight_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """Проверить, что ход является прямым (по строке или столбцу)."""
        return from_pos[0] == to_pos[0] or from_pos[1] == to_pos[1]

    def _is_path_clear(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """Проверить, что между клетками нет фигур.

        Args:
            from_pos: Начальная позиция.
            to_pos: Конечная позиция.

        Returns:
            bool: True, если все промежуточные клетки пусты.
        """
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
