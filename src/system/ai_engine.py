"""Искусственный интеллект для режима игры против компьютера."""

import random
from typing import List, Tuple, Optional

class AIEngine:
    """Движок искусственного интеллекта для игры в шахматы."""

    def __init__(self):
        self.piece_values = {
            'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0
        }
        self.search_depth = 3
        self.position_evaluated = 0

    def choose_move(self, board: list[list[str]], difficulty: int,
                   color: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Выбрать лучший ход на основе сложности."""
        self.search_depth = self._get_depth_by_difficulty(difficulty)
        legal_moves = self._get_all_legal_moves(board, color)

        if not legal_moves:
            return None

        if difficulty < 20:
            return random.choice(legal_moves)
        elif difficulty < 50:
            return self._choose_random_good_move(board, legal_moves, color)
        elif difficulty < 80:
            return self._minimax_move(board, legal_moves, color)
        else:
            return self._alpha_beta_move(board, legal_moves, color)

    def _get_depth_by_difficulty(self, difficulty: int) -> int:
        """Определить глубину поиска по сложности."""
        if difficulty < 30:
            return 1
        elif difficulty < 60:
            return 2
        elif difficulty < 85:
            return 3
        else:
            return 4

    def _get_all_legal_moves(self, board: list[list[str]],
                            color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Получить все легальные ходы для цвета."""
        moves = []
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece != "." and self._get_piece_color(piece) == color:
                    piece_moves = self._get_piece_moves(board, (row, col))
                    for to_pos in piece_moves:
                        moves.append(((row, col), to_pos))
        return moves

    def _get_piece_moves(self, board: list[list[str]],
                        pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Получить возможные ходы для фигуры."""
        # Псевдокод: генерация ходов
        return []

    def _choose_random_good_move(self, board: list[list[str]],
                                legal_moves: list, color: str) -> Tuple:
        """Выбрать случайный хороший ход."""
        scored_moves = []
        for move in legal_moves:
            score = self._evaluate_move(board, move, color)
            scored_moves.append((move, score))

        scored_moves.sort(key=lambda x: x[1], reverse=True)
        top_moves = scored_moves[:max(1, len(scored_moves) // 3)]
        return random.choice(top_moves)[0]

    def _minimax_move(self, board: list[list[str]],
                     legal_moves: list, color: str) -> Tuple:
        """Выбрать ход используя minimax."""
        best_move = None
        best_score = float('-inf')

        for move in legal_moves:
            new_board = self._make_move_copy(board, move)
            score = self._minimax(new_board, self.search_depth - 1,
                                 False, color)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move if best_move else legal_moves[0]

    def _alpha_beta_move(self, board: list[list[str]],
                        legal_moves: list, color: str) -> Tuple:
        """Выбрать ход используя alpha-beta отсечение."""
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        for move in legal_moves:
            new_board = self._make_move_copy(board, move)
            score = self._alpha_beta(new_board, self.search_depth - 1,
                                    alpha, beta, False, color)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, score)

        return best_move if best_move else legal_moves[0]

    def _minimax(self, board: list[list[str]], depth: int,
                maximizing: bool, color: str) -> float:
        """Алгоритм minimax."""
        if depth == 0:
            return self._evaluate_position(board, color)

        if maximizing:
            max_eval = float('-inf')
            moves = self._get_all_legal_moves(board, color)
            for move in moves:
                new_board = self._make_move_copy(board, move)
                eval_score = self._minimax(new_board, depth - 1, False, color)
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            min_eval = float('inf')
            opponent = "black" if color == "white" else "white"
            moves = self._get_all_legal_moves(board, opponent)
            for move in moves:
                new_board = self._make_move_copy(board, move)
                eval_score = self._minimax(new_board, depth - 1, True, color)
                min_eval = min(min_eval, eval_score)
            return min_eval

    def _alpha_beta(self, board: list[list[str]], depth: int,
                   alpha: float, beta: float, maximizing: bool,
                   color: str) -> float:
        """Алгоритм alpha-beta отсечения."""
        if depth == 0:
            return self._evaluate_position(board, color)

        if maximizing:
            max_eval = float('-inf')
            moves = self._get_all_legal_moves(board, color)
            for move in moves:
                new_board = self._make_move_copy(board, move)
                eval_score = self._alpha_beta(new_board, depth - 1,
                                             alpha, beta, False, color)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            opponent = "black" if color == "white" else "white"
            moves = self._get_all_legal_moves(board, opponent)
            for move in moves:
                new_board = self._make_move_copy(board, move)
                eval_score = self._alpha_beta(new_board, depth - 1,
                                             alpha, beta, True, color)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def _evaluate_position(self, board: list[list[str]], color: str) -> float:
        """Оценить позицию на доске."""
        score = 0.0
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece != ".":
                    piece_value = self.piece_values.get(piece.lower(), 0)
                    piece_color = self._get_piece_color(piece)
                    if piece_color == color:
                        score += piece_value
                    else:
                        score -= piece_value
        return score

    def _evaluate_move(self, board: list[list[str]],
                      move: Tuple, color: str) -> float:
        """Оценить конкретный ход."""
        from_pos, to_pos = move
        target = board[to_pos[0]][to_pos[1]]
        score = 0.0

        if target != ".":
            score += self.piece_values.get(target.lower(), 0) * 10

        if self._is_center_square(to_pos):
            score += 0.5

        return score

    def _make_move_copy(self, board: list[list[str]],
                       move: Tuple) -> list[list[str]]:
        """Создать копию доски с выполненным ходом."""
        new_board = [row[:] for row in board]
        from_pos, to_pos = move
        new_board[to_pos[0]][to_pos[1]] = new_board[from_pos[0]][from_pos[1]]
        new_board[from_pos[0]][from_pos[1]] = "."
        return new_board

    def _get_piece_color(self, piece: str) -> str:
        """Определить цвет фигуры."""
        return "white" if piece.isupper() else "black"

    def _is_center_square(self, pos: Tuple[int, int]) -> bool:
        """Проверить, является ли клетка центральной."""
        return pos[0] in [3, 4] and pos[1] in [3, 4]

    def get_hint(self, board: list[list[str]], color: str) -> Optional[Tuple]:
        """Получить подсказку для хода."""
        return self.choose_move(board, 80, color)
