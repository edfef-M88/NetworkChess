"""Базовая игровая логика шахматной партии."""

class GameLogic:
    """Управление правилами и логикой шахматной партии."""

    def __init__(self):
        self.board = self._init_board()
        self.captured_pieces = {"white": [], "black": []}

    def _init_board(self) -> list[list[str]]:
        """Инициализация начальной позиции."""
        board = [["." for _ in range(8)] for _ in range(8)]
        board[0] = ["r", "n", "b", "q", "k", "b", "n", "r"]
        board[1] = ["p"] * 8
        board[6] = ["P"] * 8
        board[7] = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        return board

    def is_checkmate(self, legal_moves: int, king_in_check: bool) -> bool:
        """Проверка мата."""
        return legal_moves == 0 and king_in_check

    def is_stalemate(self, legal_moves: int, king_in_check: bool) -> bool:
        """Проверка пата."""
        return legal_moves == 0 and not king_in_check

    def is_check(self, king_pos: tuple[int, int], color: str) -> bool:
        """Проверка шаха королю."""
        enemy_color = "black" if color == "white" else "white"
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if self._get_piece_color(piece) == enemy_color:
                    if self._can_attack(row, col, king_pos[0], king_pos[1]):
                        return True
        return False

    def get_legal_moves(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Получить все легальные ходы для фигуры."""
        moves = []
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
        """Ходы пешки: вперед на 1-2, взятие по диагонали."""
        return []

    def _get_knight_moves(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Ходы коня: L-образные."""
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                   (1, -2), (1, 2), (2, -1), (2, 1)]
        for dr, dc in offsets:
            new_row, new_col = pos[0] + dr, pos[1] + dc
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                moves.append((new_row, new_col))
        return moves

    def _get_bishop_moves(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Ходы слона: диагонали."""
        return self._get_sliding_moves(pos, [(1, 1), (1, -1), (-1, 1), (-1, -1)])

    def _get_rook_moves(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Ходы ладьи: вертикаль и горизонталь."""
        return self._get_sliding_moves(pos, [(0, 1), (0, -1), (1, 0), (-1, 0)])

    def _get_queen_moves(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Ходы ферзя: комбинация ладьи и слона."""
        return self._get_sliding_moves(pos, [(0, 1), (0, -1), (1, 0), (-1, 0),
                                              (1, 1), (1, -1), (-1, 1), (-1, -1)])

    def _get_king_moves(self, pos: tuple[int, int]) -> list[tuple[int, int]]:
        """Ходы короля: на 1 клетку в любом направлении."""
        moves = []
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                new_row, new_col = pos[0] + dr, pos[1] + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    moves.append((new_row, new_col))
        return moves

    def _get_sliding_moves(self, pos: tuple[int, int],
                          directions: list[tuple[int, int]]) -> list[tuple[int, int]]:
        """Общая логика для скользящих фигур."""
        moves = []
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

    def _can_attack(self, from_row: int, from_col: int,
                   to_row: int, to_col: int) -> bool:
        """Может ли фигура атаковать клетку."""
        return (to_row, to_col) in self.get_legal_moves((from_row, from_col))

    def _get_piece_color(self, piece: str) -> str:
        """Определить цвет фигуры."""
        if piece == ".":
            return "none"
        return "white" if piece.isupper() else "black"

    def make_move(self, from_pos: tuple[int, int], to_pos: tuple[int, int]) -> bool:
        """Выполнить ход."""
        piece = self.board[from_pos[0]][from_pos[1]]
        captured = self.board[to_pos[0]][to_pos[1]]
        if captured != ".":
            color = self._get_piece_color(piece)
            self.captured_pieces[color].append(captured)
        self.board[to_pos[0]][to_pos[1]] = piece
        self.board[from_pos[0]][from_pos[1]] = "."
        return True
