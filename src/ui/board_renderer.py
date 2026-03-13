"""Отображение шахматной доски и фигур.

Модуль содержит класс :class:`BoardRenderer`, отвечающий за визуализацию
шахматной позиции для режима локальной игры, сетевой игры и игры против ИИ.

В полноценном приложении рендерер взаимодействовал бы с графической библиотекой
(например, SDL/Pygame/Qt) и рисовал:

- фон доски и клеток с учётом темы оформления;
- фигуры (спрайты или символы);
- подсветку выбранной клетки, легальных ходов и последнего хода;
- вспомогательную разметку (координаты a–h/1–8);
- дополнительные панели (взятые фигуры, индикатор шаха и т.п.).

В данной учебной реализации часть методов представляет собой псевдокод, а для
наглядности предусмотрен вывод позиции в консоль.
"""

from typing import Optional, Tuple, List


class BoardRenderer:
    """Рендерер шахматной доски для UI-слоя.

    Класс хранит параметры отрисовки (размер клетки, тема), состояние подсветок
    и выбранной клетки, а также словари символов фигур и цветов.

    Attributes:
        theme: Название темы оформления, влияющее на цветовую схему.
        board_size: Размер доски (для шахмат — 8).
        square_size: Размер клетки в условных пикселях.
        highlighted_squares: Список координат (row, col) подсвечиваемых клеток.
        selected_square: Текущая выбранная клетка (row, col) или None.
        last_move: Последний ход (from_pos, to_pos) либо None.
        show_coordinates: Показывать ли координаты по краям доски.
        show_legal_moves: Показывать ли подсветку легальных ходов.
        piece_symbols: Соответствие символов фигур внутреннего представления и
            символов для отображения.
        colors: Цветовая схема (зависит от theme).
    """

    def __init__(self, theme: str = "classic"):
        """Создать рендерер доски и инициализировать темы/словари отображения.

        Args:
            theme: Название темы (например, "classic", "modern", "dark").

        Returns:
            None
        """
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
        """Сформировать таблицу символов фигур для отображения.

        Returns:
            dict: Словарь, где ключ — буква фигуры в модели игры, значение —
            символ (обычно Unicode) для отображения.
        """
        return {
            "K": "♔",
            "Q": "♕",
            "R": "♖",
            "B": "♗",
            "N": "♘",
            "P": "♙",
            "k": "♚",
            "q": "♛",
            "r": "♜",
            "b": "♝",
            "n": "♞",
            "p": "♟",
        }

    def _init_colors(self) -> dict:
        """Сформировать цветовую схему на основании текущей темы.

        Returns:
            dict: Словарь цветов для светлых/тёмных клеток и подсветок.
        """
        themes = {
            "classic": {
                "light_square": "#F0D9B5",
                "dark_square": "#B58863",
                "highlight": "#FFFF00",
                "selected": "#00FF00",
                "legal_move": "#90EE90",
            },
            "modern": {
                "light_square": "#EEEED2",
                "dark_square": "#769656",
                "highlight": "#BACA44",
                "selected": "#F6F669",
                "legal_move": "#BACA44",
            },
            "dark": {
                "light_square": "#4A4A4A",
                "dark_square": "#2B2B2B",
                "highlight": "#FFD700",
                "selected": "#FFA500",
                "legal_move": "#90EE90",
            },
        }
        return themes.get(self.theme, themes["classic"])

    def render(self, board_state: list[list[str]]) -> None:
        """Отрисовать доску в графическом режиме (псевдокод).

        Метод предназначен для графического UI и последовательно вызывает этапы
        отрисовки: фон, клетки, фигуры, подсветки, координаты.

        Args:
            board_state: Матрица 8×8 с фигурными символами и "." для пустых клеток.

        Returns:
            None
        """
        self._draw_board_background()
        self._draw_squares(board_state)
        self._draw_pieces(board_state)
        self._draw_highlights()
        if self.show_coordinates:
            self._draw_coordinates()

    def render_to_console(self, board_state: list[list[str]]) -> None:
        """Вывести текущую позицию в консоль в человекочитаемом виде.

        Args:
            board_state: Матрица доски 8×8.

        Returns:
            None
        """
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
        """Отрисовать одну клетку (псевдокод графической отрисовки).

        Args:
            row: Индекс строки (0..7).
            col: Индекс столбца (0..7).
            board_state: Текущее состояние доски.

        Returns:
            None
        """
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
        """Добавить клетку в список подсветки.

        Args:
            row: Индекс строки клетки.
            col: Индекс столбца клетки.

        Returns:
            None
        """
        if (row, col) not in self.highlighted_squares:
            self.highlighted_squares.append((row, col))

    def unhighlight_square(self, row: int, col: int) -> None:
        """Убрать подсветку с указанной клетки.

        Args:
            row: Индекс строки клетки.
            col: Индекс столбца клетки.

        Returns:
            None
        """
        if (row, col) in self.highlighted_squares:
            self.highlighted_squares.remove((row, col))

    def clear_highlights(self) -> None:
        """Очистить список всех подсвеченных клеток.

        Returns:
            None
        """
        self.highlighted_squares.clear()

    def select_square(self, row: int, col: int) -> None:
        """Отметить клетку как выбранную пользователем.

        Args:
            row: Индекс строки.
            col: Индекс столбца.

        Returns:
            None
        """
        self.selected_square = (row, col)

    def deselect_square(self) -> None:
        """Снять выделение выбранной клетки.

        Returns:
            None
        """
        self.selected_square = None

    def show_legal_moves_for_square(self, row: int, col: int, legal_moves: List[Tuple[int, int]]) -> None:
        """Подсветить набор легальных ходов для выбранной клетки.

        Args:
            row: Строка выбранной клетки (для контекста UI).
            col: Столбец выбранной клетки (для контекста UI).
            legal_moves: Список целевых клеток (row, col), куда разрешено ходить.

        Returns:
            None
        """
        if self.show_legal_moves:
            self.clear_highlights()
            for move in legal_moves:
                self.highlight_square(move[0], move[1])

    def highlight_last_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> None:
        """Подсветить последний сделанный ход на доске.

        Args:
            from_pos: Координаты исходной клетки (row, col).
            to_pos: Координаты целевой клетки (row, col).

        Returns:
            None
        """
        self.last_move = (from_pos, to_pos)
        self.highlight_square(from_pos[0], from_pos[1])
        self.highlight_square(to_pos[0], to_pos[1])

    def set_theme(self, theme_name: str) -> bool:
        """Переключить тему оформления рендерера.

        Args:
            theme_name: Имя темы ("classic"/"modern"/"dark").

        Returns:
            bool: True, если тема применена и цветовая схема обновлена.
        """
        if theme_name in ["classic", "modern", "dark"]:
            self.theme = theme_name
            self.colors = self._init_colors()
            return True
        return False

    def toggle_coordinates(self) -> None:
        """Включить/выключить отображение координат доски.

        Returns:
            None
        """
        self.show_coordinates = not self.show_coordinates

    def toggle_legal_moves_display(self) -> None:
        """Включить/выключить подсветку легальных ходов.

        Returns:
            None
        """
        self.show_legal_moves = not self.show_legal_moves

    def get_square_at_position(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """Преобразовать пиксельные координаты в координаты клетки.

        Args:
            x: Координата X в условных пикселях.
            y: Координата Y в условных пикселях.

        Returns:
            Optional[Tuple[int, int]]: (row, col) если точка попадает на доску,
            иначе None.
        """
        col = x // self.square_size
        row = y // self.square_size
        if 0 <= row < 8 and 0 <= col < 8:
            return (row, col)
        return None

    def get_square_center(self, row: int, col: int) -> Tuple[int, int]:
        """Получить координаты центра клетки в пикселях.

        Args:
            row: Индекс строки клетки.
            col: Индекс столбца клетки.

        Returns:
            Tuple[int, int]: (x, y) центра клетки.
        """
        x = col * self.square_size + self.square_size // 2
        y = row * self.square_size + self.square_size // 2
        return (x, y)

    def animate_move(
        self,
        from_pos: Tuple[int, int],
        to_pos: Tuple[int, int],
        piece: str,
        duration_ms: int = 300,
    ) -> None:
        """Анимировать перемещение фигуры между двумя клетками (псевдокод).

        Args:
            from_pos: Исходная клетка (row, col).
            to_pos: Целевая клетка (row, col).
            piece: Символ перемещаемой фигуры.
            duration_ms: Длительность анимации в миллисекундах.

        Returns:
            None
        """
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
        """Показать диалог выбора фигуры при превращении пешки.

        Args:
            color: Цвет стороны, выполняющей превращение ("white"/"black").

        Returns:
            str: Символ выбранной фигуры (например, "Q" или "q").
        """
        pieces = ["Q", "R", "B", "N"] if color == "white" else ["q", "r", "b", "n"]
        # Псевдокод: показать диалог выбора
        return pieces[0]  # По умолчанию ферзь

    def draw_check_indicator(self, king_pos: Tuple[int, int]) -> None:
        """Показать индикатор шаха для указанного короля.

        Args:
            king_pos: Координаты короля (row, col).

        Returns:
            None
        """
        # Псевдокод: нарисовать красную рамку вокруг короля
        self.highlight_square(king_pos[0], king_pos[1])

    def draw_captured_pieces(self, captured_white: List[str], captured_black: List[str]) -> None:
        """Отобразить списки взятых фигур у белых и чёрных.

        Args:
            captured_white: Список символов фигур, взятых у белых.
            captured_black: Список символов фигур, взятых у чёрных.

        Returns:
            None
        """
        # Псевдокод: показать взятые фигуры сбоку от доски
        print(f"Взято белых: {' '.join(self.piece_symbols.get(p, p) for p in captured_white)}")
        print(f"Взято черных: {' '.join(self.piece_symbols.get(p, p) for p in captured_black)}")

    def _draw_board_background(self) -> None:
        """Нарисовать фон доски (псевдокод).

        Returns:
            None
        """
        # Псевдокод: нарисовать фон
        pass

    def _draw_squares(self, board_state: list[list[str]]) -> None:
        """Нарисовать все клетки доски.

        Args:
            board_state: Матрица позиции.

        Returns:
            None
        """
        for row in range(8):
            for col in range(8):
                self.render_square(row, col, board_state)

    def _draw_pieces(self, board_state: list[list[str]]) -> None:
        """Нарисовать все фигуры, присутствующие на доске.

        Args:
            board_state: Матрица позиции.

        Returns:
            None
        """
        for row in range(8):
            for col in range(8):
                piece = board_state[row][col]
                if piece != ".":
                    x = col * self.square_size
                    y = row * self.square_size
                    self._draw_piece(piece, x, y)

    def _draw_piece(self, piece: str, x: int, y: int) -> None:
        """Нарисовать одну фигуру в указанных координатах (псевдокод).

        Args:
            piece: Символ фигуры.
            x: Координата X в пикселях.
            y: Координата Y в пикселях.

        Returns:
            None
        """
        # Псевдокод: загрузить спрайт фигуры и нарисовать
        _symbol = self.piece_symbols.get(piece, piece)
        # Отрисовать symbol в позиции (x, y)

    def _draw_highlights(self) -> None:
        """Нарисовать подсветки выбранных/доступных клеток (псевдокод).

        Returns:
            None
        """
        for _row, _col in self.highlighted_squares:
            # Псевдокод: нарисовать полупрозрачный круг или рамку
            pass

    def _draw_coordinates(self) -> None:
        """Нарисовать координатную разметку по краям доски (псевдокод).

        Returns:
            None
        """
        # Псевдокод: нарисовать буквы a-h и цифры 1-8
        files = "abcdefgh"
        ranks = "87654321"
        # Отрисовать координаты по краям доски

    def _draw_rectangle(self, x: int, y: int, width: int, height: int, color: str) -> None:
        """Нарисовать прямоугольник (примитив для отрисовки клетки).

        Args:
            x: Координата X.
            y: Координата Y.
            width: Ширина.
            height: Высота.
            color: Цвет (например, HEX-строка).

        Returns:
            None
        """
        # Псевдокод: использовать графическую библиотеку для рисования
        pass

    def flip_board(self) -> None:
        """Перевернуть доску (например, при игре за чёрных).

        Returns:
            None
        """
        # Псевдокод: изменить порядок отрисовки
        pass

    def export_as_image(self, board_state: list[list[str]], filename: str) -> bool:
        """Экспортировать позицию как изображение (заглушка).

        Args:
            board_state: Матрица позиции 8×8.
            filename: Путь к файлу изображения.

        Returns:
            bool: True, если экспорт считается успешным.
        """
        # Псевдокод: сохранить текущее состояние доски в файл
        return True

    def get_fen_diagram(self, board_state: list[list[str]]) -> str:
        """Получить текстовую (ASCII) диаграмму позиции для отчёта/лога.

        Метод полезен для журналирования, тестов и отладочной печати позиции.

        Args:
            board_state: Матрица позиции 8×8.

        Returns:
            str: Многострочная строка, представляющая позицию.
        """
        diagram = ""
        for row in board_state:
            diagram += " ".join(self.piece_symbols.get(p, p) if p != "." else "·" for p in row)
            diagram += "\n"
        return diagram
