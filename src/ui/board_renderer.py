"""Отображение шахматной доски и фигур."""

from typing import Optional, Tuple, List

class BoardRenderer:
    """Рендеринг шахматной доски."""

    def __init__(self, theme: str = "classic"):
        self.theme = theme
        self.board_size = 8
        self.square_size = 80
        self.highlighted_squares = []
        self.selected_square = None
        self.last_move = None
        self.show_coordinates = True
        self.show_legal_moves = True
        self.piece_symbols = self._init_piece_symbols()
        self.colors = self._init_colors()

    def _init_piece_symbols(self) -> dict:
        """Инициализировать символы фигур."""
        return {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
        }

    def _init_colors(self) -> dict:
        """Инициализировать цветовую схему."""
        themes = {
            "classic": {
                "light_square": "#F0D9B5",
                "dark_square": "#B58863",
                "highlight": "#FFFF00",
                "selected": "#00FF00",
                "legal_move": "#90EE90"
            },
            "modern": {
                "light_square": "#EEEED2",
                "dark_square": "#769656",
                "highlight": "#BACA44",
                "selected": "#F6F669",
                "legal_move": "#BACA44"
            },
            "dark": {
                "light_square": "#4A4A4A",
                "dark_square": "#2B2B2B",
                "highlight": "#FFD700",
                "selected": "#FFA500",
                "legal_move": "#90EE90"
            }
        }
        return themes.get(self.theme, themes["classic"])

    def render(self, board_state: list[list[str]]) -> None:
        """Отрисовать доску."""
        self._draw_board_background()
        self._draw_squares(board_state)
        self._draw_pieces(board_state)
        self._draw_highlights()
        if self.show_coordinates:
            self._draw_coordinates()

    def render_to_console(self, board_state: list[list[str]]) -> None:
        """Отрисовать доску в консоль."""
        print("\n  a b c d e f g h")
        for i, row in enumerate(board_state):
            row_num = 8 - i
            pieces = []
            for piece in row:
                if piece == ".":
                    pieces.append(".")
                else:
                    pieces.append(self.piece_symbols.get(piece, piece))
            print(f"{row_num} {' '.join(pieces)} {row_num}")
        print("  a b c d e f g h\n")

    def render_square(self, row: int, col: int, board_state: list[list[str]]) -> None:
        """Отрисовать одну клетку."""
        x = col * self.square_size
        y = row * self.square_size

        # Определить цвет клетки
        is_light = (row + col) % 2 == 0
        color = self.colors["light_square"] if is_light else self.colors["dark_square"]

        # Проверить подсветку
        if (row, col) in self.highlighted_squares:
            color = self.colors["highlight"]
        elif self.selected_square == (row, col):
            color = self.colors["selected"]

        # Псевдокод: нарисовать квадрат
        self._draw_rectangle(x, y, self.square_size, self.square_size, color)

        # Нарисовать фигуру
        piece = board_state[row][col]
        if piece != ".":
            self._draw_piece(piece, x, y)

    def highlight_square(self, row: int, col: int) -> None:
        """Подсветить клетку."""
        if (row, col) not in self.highlighted_squares:
            self.highlighted_squares.append((row, col))

    def unhighlight_square(self, row: int, col: int) -> None:
        """Убрать подсветку с клетки."""
        if (row, col) in self.highlighted_squares:
            self.highlighted_squares.remove((row, col))

    def clear_highlights(self) -> None:
        """Очистить все подсветки."""
        self.highlighted_squares.clear()

    def select_square(self, row: int, col: int) -> None:
        """Выбрать клетку."""
        self.selected_square = (row, col)

    def deselect_square(self) -> None:
        """Снять выделение."""
        self.selected_square = None

    def show_legal_moves_for_square(self, row: int, col: int,
                                   legal_moves: List[Tuple[int, int]]) -> None:
        """Показать легальные ходы для клетки."""
        if self.show_legal_moves:
            self.clear_highlights()
            for move in legal_moves:
                self.highlight_square(move[0], move[1])

    def highlight_last_move(self, from_pos: Tuple[int, int],
                          to_pos: Tuple[int, int]) -> None:
        """Подсветить последний ход."""
        self.last_move = (from_pos, to_pos)
        self.highlight_square(from_pos[0], from_pos[1])
        self.highlight_square(to_pos[0], to_pos[1])

    def set_theme(self, theme_name: str) -> bool:
        """Установить тему."""
        if theme_name in ["classic", "modern", "dark"]:
            self.theme = theme_name
            self.colors = self._init_colors()
            return True
        return False

    def toggle_coordinates(self) -> None:
        """Переключить отображение координат."""
        self.show_coordinates = not self.show_coordinates

    def toggle_legal_moves_display(self) -> None:
        """Переключить отображение легальных ходов."""
        self.show_legal_moves = not self.show_legal_moves

    def get_square_at_position(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Получить клетку по координатам пикселей."""
        col = x // self.square_size
        row = y // self.square_size
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None

    def get_square_center(self, row: int, col: int) -> Tuple[int, int]:
        """Получить центр клетки в пикселях."""
        x = col * self.square_size + self.square_size // 2
        y = row * self.square_size + self.square_size // 2
        return (x, y)

    def animate_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int],
                    piece: str, duration_ms: int = 300) -> None:
        """Анимировать ход."""
        # Псевдокод: плавное перемещение фигуры
        start_x, start_y = self.get_square_center(from_pos[0], from_pos[1])
        end_x, end_y = self.get_square_center(to_pos[0], to_pos[1])

        # Интерполяция позиции за duration_ms миллисекунд
        steps = 30
        for step in range(steps):
            progress = step / steps
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress
            # Отрисовать фигуру в текущей позиции

    def draw_promotion_dialog(self, color: str) -> str:
        """Показать диалог выбора фигуры при превращении пешки."""
        pieces = ['Q', 'R', 'B', 'N'] if color == "white" else ['q', 'r', 'b', 'n']
        # Псевдокод: показать диалог выбора
        return pieces[0]  # По умолчанию ферзь

    def draw_check_indicator(self, king_pos: Tuple[int, int]) -> None:
        """Показать индикатор шаха."""
        # Псевдокод: нарисовать красную рамку вокруг короля
        self.highlight_square(king_pos[0], king_pos[1])

    def draw_captured_pieces(self, captured_white: List[str],
                            captured_black: List[str]) -> None:
        """Отрисовать взятые фигуры."""
        # Псевдокод: показать взятые фигуры сбоку от доски
        print(f"Взято белых: {' '.join(self.piece_symbols.get(p, p) for p in captured_white)}")
        print(f"Взято черных: {' '.join(self.piece_symbols.get(p, p) for p in captured_black)}")

    def _draw_board_background(self) -> None:
        """Нарисовать фон доски."""
        # Псевдокод: нарисовать фон
        pass

    def _draw_squares(self, board_state: list[list[str]]) -> None:
        """Нарисовать все клетки."""
        for row in range(8):
            for col in range(8):
                self.render_square(row, col, board_state)

    def _draw_pieces(self, board_state: list[list[str]]) -> None:
        """Нарисовать все фигуры."""
        for row in range(8):
            for col in range(8):
                piece = board_state[row][col]
                if piece != ".":
                    x = col * self.square_size
                    y = row * self.square_size
                    self._draw_piece(piece, x, y)

    def _draw_piece(self, piece: str, x: int, y: int) -> None:
        """Нарисовать фигуру."""
        # Псевдокод: загрузить спрайт фигуры и нарисовать
        symbol = self.piece_symbols.get(piece, piece)
        # Отрисовать symbol в позиции (x, y)

    def _draw_highlights(self) -> None:
        """Нарисовать подсветки."""
        for row, col in self.highlighted_squares:
            # Псевдокод: нарисовать полупрозрачный круг или рамку
            pass

    def _draw_coordinates(self) -> None:
        """Нарисовать координаты."""
        # Псевдокод: нарисовать буквы a-h и цифры 1-8
        files = "abcdefgh"
        ranks = "87654321"
        # Отрисовать координаты по краям доски

    def _draw_rectangle(self, x: int, y: int, width: int, height: int,
                       color: str) -> None:
        """Нарисовать прямоугольник."""
        # Псевдокод: использовать графическую библиотеку для рисования
        pass

    def flip_board(self) -> None:
        """Перевернуть доску (для игры за черных)."""
        # Псевдокод: изменить порядок отрисовки
        pass

    def export_as_image(self, board_state: list[list[str]],
                       filename: str) -> bool:
        """Экспортировать доску как изображение."""
        # Псевдокод: сохранить текущее состояние доски в файл
        return True

    def get_fen_diagram(self, board_state: list[list[str]]) -> str:
        """Получить ASCII диаграмму позиции."""
        diagram = ""
        for row in board_state:
            diagram += " ".join(self.piece_symbols.get(p, p) if p != "." else "·" for p in row)
            diagram += "\n"
        return diagram
