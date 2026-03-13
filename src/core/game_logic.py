"""Игровая логика шахматной партии.

Модуль содержит упрощённую реализацию операций над шахматной доской:
инициализация стартовой позиции, генерация «легальных» ходов для базовых
типов фигур, а также элементарные проверки шаха/мата/пата.

Важно: реализация носит учебный характер и не покрывает все тонкости правил
шахмат (например, взятие на проходе, превращение, рокировка, корректная
фильтрация ходов, оставляющих короля под шахом).

Classes:
    GameLogic: Управляет доской и базовыми правилами.
"""


class GameLogic:
    """Управление правилами и логикой шахматной партии.

    Класс хранит текущее состояние доски (матрица 8×8) и список взятых фигур,
    а также предоставляет методы для получения возможных ходов и выполнения хода.

    Attributes:
        board: Двумерный список 8×8, представляющий доску. Пустая клетка — ".".
        captured_pieces: Словарь со списками взятых фигур по цветам.
    """

    def __init__(self):
        """Создать объект игровой логики и подготовить стартовую позицию."""
        self.board = self._init_board()
        self.captured_pieces = {"white": [], "black": []}

    def _init_board(self) -> list[list[str]]:
        """Инициализировать стартовую расстановку фигур.

        Returns:
            list[list[str]]: Матрица 8×8 со стартовой позицией.
        """
        board = [["." for _ in range(8)] for _ in range(8)]
        board[0] = ["r", "n", "b", "q", "k", "b", "n", "r"]
        board[1] = ["p"] * 8
        board[6] = ["P"] * 8
        board[7] = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        return board

    def is_checkmate(self, legal_moves: int, king_in_check: bool) -> bool:
        """Проверить условие мата по числу ходов и факту шаха.

        Args:
            legal_moves: Количество доступных легальных ходов.
            king_in_check: Находится ли король под шахом.

        Returns:
            bool: True, если ходов нет и король под шахом.
        """
        return legal_moves == 0 and king_in_check

    def is_stalemate(self, legal_moves: int, king_in_check: bool) -> bool:
        """Проверить условие пата по числу ходов и факту шаха.

        Args:
            legal_moves: Количество доступных легальных ходов.
            king_in_check: Находится ли король под шахом.

        Returns:
            bool: True, если ходов нет и король НЕ под шахом.
        """
        return legal_moves == 0 and not king_in_check

    def is_check(self, king_pos: tuple[int, int], color: str) -> bool:
        """Проверить, находится ли король указанного цвета под шахом.

        Метод перебирает фигуры противника и проверяет, может ли какая-либо из
        них атаковать клетку короля.

        Args:
            king_pos: Координаты короля (row, col).
            color: Цвет короля ("white" или "black").

        Returns:
            bool: True, если есть атакующая фигура.
        """
        enemy_color = "black" if color == "white" else "white"
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if self._get_piece_color(piece) == enemy_color:
                    if self._can_attack(row, col, king_pos[0], king_pos[1]):
                        return True
        return False

    def get_legal_moves(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Получить список возможных ходов для фигуры в указанной клетке.

        Args:
            pos: Координаты фигуры (row, col).

        Returns:
            list[tuple[int, int]]: Список целевых клеток (row, col).
        """
        moves: list[tuple[int, int]] = []
        piece = self.board[pos[0]][pos[1]]
        if piece.lower() == "p":
            moves = self._get_pawn_moves(pos)
        elif piece.lower() == "n":
            moves = self._get_knight_moves(pos)
        elif piece.lower() == "b":
            moves = self._get_bishop_moves(pos)
        elif piece.lower() == "r":
            moves = self._get_rook_moves(pos)
        elif piece.lower() == "q":
            moves = self._get_queen_moves(pos)
        elif piece.lower() == "k":
            moves = self._get_king_moves(pos)
        return moves

    def _get_pawn_moves(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Сгенерировать ходы пешки.

        Args:
            pos: Координаты пешки (row, col).

        Returns:
            list[tuple[int, int]]: Возможные ходы пешки.
        """
        return []

    def _get_knight_moves(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Сгенерировать ходы коня (L-образные смещения).

        Args:
            pos: Координаты коня (row, col).

        Returns:
            list[tuple[int, int]]: Возможные ходы коня в пределах доски.
        """
        moves: list[tuple[int, int]] = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            new_row, new_col = pos[0] + dr, pos[1] + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                moves.append((new_row, new_col))
        return moves

    def _get_bishop_moves(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Сгенерировать ходы слона по диагоналям.

        Args:
            pos: Координаты слона (row, col).

        Returns:
            list[tuple[int, int]]: Список клеток, достижимых по диагоналям.
        """
        return self._get_sliding_moves(pos, [(1, 1), (1, -1), (-1, 1), (-1, -1)])

    def _get_rook_moves(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Сгенерировать ходы ладьи по вертикали/горизонтали.

        Args:
            pos: Координаты ладьи (row, col).

        Returns:
            list[tuple[int, int]]: Список клеток, достижимых по прямым.
        """
        return self._get_sliding_moves(pos, [(0, 1), (0, -1), (1, 0), (-1, 0)])

    def _get_queen_moves(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Сгенерировать ходы ферзя (как у ладьи и слона).

        Args:
            pos: Координаты ферзя (row, col).

        Returns:
            list[tuple[int, int]]: Список клеток, достижимых по прямым и диагоналям.
        """
        return self._get_sliding_moves(pos, [(0, 1), (0, -1), (1, 0), (-1, 0),
                                              (1, 1), (1, -1), (-1, 1), (-1, -1)])

    def _get_king_moves(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Сгенерировать ходы короля (на 1 клетку).

        Args:
            pos: Координаты короля (row, col).

        Returns:
            list[tuple[int, int]]: Возможные ходы короля в пределах доски.
        """
        moves: list[tuple[int, int]] = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = pos[0] + dr, pos[1] + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    moves.append((new_row, new_col))
        return moves

    def _get_sliding_moves(
        self,
        pos: tuple[int, int],
        directions: list[tuple[int, int]],
    ) -> list[tuple[int, int]]:
        """Общая логика ходов «скользящих» фигур.

        Скользящие фигуры (слон, ладья, ферзь) могут двигаться по направлению,
        пока не встретят границу доски или фигуру.

        Args:
            pos: Начальная позиция фигуры.
            directions: Список направлений (dr, dc).

        Returns:
            list[tuple[int, int]]: Список достижимых клеток.
        """
        moves: list[tuple[int, int]] = []
        for dr, dc in directions:
            row, col = pos[0] + dr, pos[1] + dc
            while 0 <= row < 8 and 0 <= col < 8:
                if self.board[row][col] == ".":
                    moves.append((row, col))
                else:
                    moves.append((row, col))
                    break
                row += dr
                col += dc
        return moves

    def _can_attack(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """Проверить, может ли фигура атаковать целевую клетку.

        Args:
            from_row: Начальная строка.
            from_col: Начальный столбец.
            to_row: Целевая строка.
            to_col: Целевой столбец.

        Returns:
            bool: True, если целевая клетка входит в список возможных ходов.
        """
        return (to_row, to_col) in self.get_legal_moves((from_row, from_col))

    def _get_piece_color(self, piece: str) -> str:
        """Определить цвет фигуры по символу.

        Args:
            piece: Символ фигуры (буква) или "." для пустой клетки.

        Returns:
            str: "white", "black" или "none".
        """
        if piece == ".":
            return "none"
        return "white" if piece.isupper() else "black"

    def make_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """Выполнить ход и обновить доску.

        Метод переносит фигуру, а при необходимости сохраняет взятую фигуру
        в списке captured_pieces соответствующего цвета.

        Args:
            from_pos: Начальная позиция фигуры.
            to_pos: Конечная позиция фигуры.

        Returns:
            bool: True, если ход был выполнен.
        """
        piece = self.board[from_pos[0]][from_pos[1]]
        captured = self.board[to_pos[0]][to_pos[1]]
        if captured != ".":
            color = self._get_piece_color(piece)
            self.captured_pieces[color].append(captured)
        self.board[to_pos[0]][to_pos[1]] = piece
        self.board[from_pos[0]][from_pos[1]] = "."
        return True
