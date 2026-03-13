"""Движок искусственного интеллекта (AI) для игры против компьютера.

Модуль содержит класс :class:`AIEngine`, который выбирает ход для стороны
компьютера на основе уровня сложности 1–100.

В рамках учебного проекта поддерживается несколько стратегий выбора хода:

- низкие уровни: случайный выбор из доступных ходов;
- средние уровни: эвристический отбор «хороших» ходов по простой оценке;
- высокие уровни: поисковые алгоритмы minimax и alpha-beta (упрощённо).

Важно: генерация ходов и оценка позиции в текущей версии носят демонстрационный
характер (часть методов является заглушками), однако структура кода отражает
типичный подход к построению шахматного AI.
"""

import random
from typing import List, Tuple, Optional


class AIEngine:
    """AI-движок для выбора ходов в режиме одиночной игры.

    Экземпляр хранит базовые веса фигур для оценки (material), параметры глубины
    поиска и счётчик оценённых позиций.

    Attributes:
        piece_values: Стоимости фигур для оценки материального перевеса.
        search_depth: Текущая глубина поиска (зависит от сложности).
        position_evaluated: Счётчик позиций, оценённых в ходе поиска.
    """

    def __init__(self):
        """Инициализировать AI-движок со значениями по умолчанию.

        Returns:
            None
        """
        self.piece_values = {"p": 1, "n": 3, "b": 3, "r": 5, "q": 9, "k": 0}
        self.search_depth = 3
        self.position_evaluated = 0

    def choose_move(
        self,
        board: list[list[str]],
        difficulty: int,
        color: str,
    ) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Выбрать ход для заданного цвета с учётом уровня сложности.

        Алгоритм выбора зависит от параметра difficulty:
        - < 20: случайный ход;
        - 20..49: случайный выбор среди эвристически «неплохих» ходов;
        - 50..79: minimax;
        - >= 80: alpha-beta.

        Args:
            board: Матрица доски 8×8 ("." — пустая клетка).
            difficulty: Уровень сложности 1–100.
            color: Цвет стороны, за которую играет AI ("white"/"black").

        Returns:
            Optional[Tuple[Tuple[int, int], Tuple[int, int]]]: Ход в виде
            ((from_row, from_col), (to_row, to_col)) либо None, если ходов нет.
        """
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
        """Определить глубину поиска по уровню сложности.

        Args:
            difficulty: Уровень сложности 1–100.

        Returns:
            int: Глубина поиска (в полуходах), используемая алгоритмами minimax/alpha-beta.
        """
        if difficulty < 30:
            return 1
        elif difficulty < 60:
            return 2
        elif difficulty < 85:
            return 3
        else:
            return 4

    def _get_all_legal_moves(
        self,
        board: list[list[str]],
        color: str,
    ) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Собрать все доступные ходы для указанного цвета.

        Метод перебирает все клетки доски, находит фигуры нужного цвета и
        запрашивает их ходы через `_get_piece_moves`.

        Args:
            board: Матрица доски 8×8.
            color: Цвет стороны ("white"/"black").

        Returns:
            List[Tuple[Tuple[int, int], Tuple[int, int]]]: Список ходов
            ((from_row, from_col), (to_row, to_col)).
        """
        moves = []
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece != "." and self._get_piece_color(piece) == color:
                    piece_moves = self._get_piece_moves(board, (row, col))
                    for to_pos in piece_moves:
                        moves.append(((row, col), to_pos))
        return moves

    def _get_piece_moves(self, board: list[list[str]], pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Получить список возможных ходов конкретной фигуры (заглушка).

        В полноценной реализации метод должен учитывать тип фигуры, препятствия,
        очередность, шах королю и другие правила.

        Args:
            board: Матрица доски 8×8.
            pos: Координаты фигуры (row, col).

        Returns:
            List[Tuple[int, int]]: Список целевых клеток, достижимых с `pos`.
        """
        # Псевдокод: генерация ходов
        return []

    def _choose_random_good_move(self, board: list[list[str]], legal_moves: list, color: str) -> Tuple:
        """Выбрать случайный ход среди лучших по эвристической оценке.

        Метод оценивает каждый ход функцией `_evaluate_move`, сортирует по
        убыванию и выбирает случайный ход из верхней трети.

        Args:
            board: Текущее состояние доски.
            legal_moves: Список доступных ходов.
            color: Цвет стороны AI.

        Returns:
            Tuple: Выбранный ход в формате ((from_row, from_col), (to_row, to_col)).
        """
        scored_moves = []
        for move in legal_moves:
            score = self._evaluate_move(board, move, color)
            scored_moves.append((move, score))

        scored_moves.sort(key=lambda x: x[1], reverse=True)
        top_moves = scored_moves[: max(1, len(scored_moves) // 3)]
        return random.choice(top_moves)[0]

    def _minimax_move(self, board: list[list[str]], legal_moves: list, color: str) -> Tuple:
        """Выбрать ход с помощью алгоритма minimax.

        Args:
            board: Текущее состояние доски.
            legal_moves: Список доступных ходов.
            color: Цвет стороны AI.

        Returns:
            Tuple: Лучший ход по оценке minimax (или первый ход как fallback).
        """
        best_move = None
        best_score = float("-inf")

        for move in legal_moves:
            new_board = self._make_move_copy(board, move)
            score = self._minimax(new_board, self.search_depth - 1, False, color)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move if best_move else legal_moves[0]

    def _alpha_beta_move(self, board: list[list[str]], legal_moves: list, color: str) -> Tuple:
        """Выбрать ход с помощью alpha-beta отсечения.

        Args:
            board: Текущее состояние доски.
            legal_moves: Список доступных ходов.
            color: Цвет стороны AI.

        Returns:
            Tuple: Лучший ход по alpha-beta (или первый ход как fallback).
        """
        best_move = None
        best_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        for move in legal_moves:
            new_board = self._make_move_copy(board, move)
            score = self._alpha_beta(new_board, self.search_depth - 1, alpha, beta, False, color)
            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, score)

        return best_move if best_move else legal_moves[0]

    def _minimax(self, board: list[list[str]], depth: int, maximizing: bool, color: str) -> float:
        """Рекурсивный алгоритм minimax для оценки позиции.

        Args:
            board: Доска в текущем узле дерева поиска.
            depth: Оставшаяся глубина поиска.
            maximizing: True для максимизирующего игрока, False для минимизирующего.
            color: Цвет стороны AI (для которой вычисляется оценка позиции).

        Returns:
            float: Оценка позиции.
        """
        if depth == 0:
            return self._evaluate_position(board, color)

        if maximizing:
            max_eval = float("-inf")
            moves = self._get_all_legal_moves(board, color)
            for move in moves:
                new_board = self._make_move_copy(board, move)
                eval_score = self._minimax(new_board, depth - 1, False, color)
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            min_eval = float("inf")
            opponent = "black" if color == "white" else "white"
            moves = self._get_all_legal_moves(board, opponent)
            for move in moves:
                new_board = self._make_move_copy(board, move)
                eval_score = self._minimax(new_board, depth - 1, True, color)
                min_eval = min(min_eval, eval_score)
            return min_eval

    def _alpha_beta(
        self,
        board: list[list[str]],
        depth: int,
        alpha: float,
        beta: float,
        maximizing: bool,
        color: str,
    ) -> float:
        """Алгоритм minimax с alpha-beta отсечением.

        Args:
            board: Доска в текущем узле.
            depth: Оставшаяся глубина поиска.
            alpha: Нижняя граница лучшей оценки для максимизатора.
            beta: Верхняя граница лучшей оценки для минимизатора.
            maximizing: Признак максимизирующего шага.
            color: Цвет стороны AI.

        Returns:
            float: Оценка позиции.
        """
        if depth == 0:
            return self._evaluate_position(board, color)

        if maximizing:
            max_eval = float("-inf")
            moves = self._get_all_legal_moves(board, color)
            for move in moves:
                new_board = self._make_move_copy(board, move)
                eval_score = self._alpha_beta(new_board, depth - 1, alpha, beta, False, color)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float("inf")
            opponent = "black" if color == "white" else "white"
            moves = self._get_all_legal_moves(board, opponent)
            for move in moves:
                new_board = self._make_move_copy(board, move)
                eval_score = self._alpha_beta(new_board, depth - 1, alpha, beta, True, color)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval

    def _evaluate_position(self, board: list[list[str]], color: str) -> float:
        """Оценить позицию на доске по материальному балансу.

        Args:
            board: Матрица позиции 8×8.
            color: Цвет стороны AI.

        Returns:
            float: Оценка (положительная — преимущество AI).
        """
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

    def _evaluate_move(self, board: list[list[str]], move: Tuple, color: str) -> float:
        """Оценить конкретный ход по простым эвристикам.

        В текущей версии учитывается:
        - взятие фигуры (с приоритетом по стоимости цели);
        - контроль центральных полей.

        Args:
            board: Текущее состояние доски.
            move: Ход в формате ((from_row, from_col), (to_row, to_col)).
            color: Цвет стороны AI.

        Returns:
            float: Эвристическая оценка хода.
        """
        _from_pos, to_pos = move
        target = board[to_pos[0]][to_pos[1]]
        score = 0.0

        if target != ".":
            score += self.piece_values.get(target.lower(), 0) * 10

        if self._is_center_square(to_pos):
            score += 0.5

        return score

    def _make_move_copy(self, board: list[list[str]], move: Tuple) -> list[list[str]]:
        """Создать копию доски и применить к ней ход.

        Args:
            board: Исходная матрица доски.
            move: Ход, который нужно применить.

        Returns:
            list[list[str]]: Новая матрица доски.
        """
        new_board = [row[:] for row in board]
        from_pos, to_pos = move
        new_board[to_pos[0]][to_pos[1]] = new_board[from_pos[0]][from_pos[1]]
        new_board[from_pos[0]][from_pos[1]] = "."
        return new_board

    def _get_piece_color(self, piece: str) -> str:
        """Определить цвет фигуры по регистру символа.

        Args:
            piece: Символ фигуры.

        Returns:
            str: "white" для верхнего регистра, иначе "black".
        """
        return "white" if piece.isupper() else "black"

    def _is_center_square(self, pos: Tuple[int, int]) -> bool:
        """Проверить, относится ли клетка к центральным полям.

        Args:
            pos: Координаты клетки (row, col).

        Returns:
            bool: True, если клетка лежит в квадрате 2×2 в центре доски.
        """
        return pos[0] in [3, 4] and pos[1] in [3, 4]

    def get_hint(self, board: list[list[str]], color: str) -> Optional[Tuple]:
        """Получить «подсказку» хода (рекомендацию) для указанного цвета.

        В текущей реализации подсказка равна выбору хода на фиксированной
        высокой сложности.

        Args:
            board: Состояние доски.
            color: Цвет стороны ("white"/"black").

        Returns:
            Optional[Tuple]: Рекомендуемый ход либо None.
        """
        return self.choose_move(board, 80, color)
