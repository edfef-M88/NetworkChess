"""Состояние шахматной партии.

Модуль описывает объект, отвечающий за «метаданные» партии: чей сейчас ход,
история ходов, счётчики для правил (например, правило 50 ходов), права на
рокировку, клетка для взятия на проходе и итоговый результат.

Classes:
    GameState: Контейнер состояния партии и вспомогательные операции.
"""


class GameState:
    """Управление состоянием игры.

    Объект не выполняет глубокую валидацию ходов; он аккумулирует информацию,
    которую удобно хранить отдельно от доски и логики генерации ходов.

    Attributes:
        current_turn: Цвет, который должен ходить следующим ("white"/"black").
        move_history: Список ходов в строковой форме.
        move_count: Количество полуходов/ходов (в данной учебной реализации).
        halfmove_clock: Счётчик полуходов для правила 50 ходов.
        castling_rights: Права на рокировку по цветам и флангам.
        en_passant_target: Клетка (row, col), доступная для взятия на проходе.
        game_result: Строка результата (например, "1-0"), либо None.
    """

    def __init__(self) -> None:
        """Создать объект состояния партии со значениями по умолчанию."""
        self.current_turn = "white"
        self.move_history: list[str] = []
        self.move_count = 0
        self.halfmove_clock = 0
        self.castling_rights = {
            "white": {"kingside": True, "queenside": True},
            "black": {"kingside": True, "queenside": True},
        }
        self.en_passant_target = None
        self.game_result = None

    def add_move(self, move: str) -> None:
        """Добавить ход в историю и обновить счётчики.

        Args:
            move: Ход в выбранной строковой нотации.

        Returns:
            None
        """
        self.move_history.append(move)
        self.move_count += 1
        self.halfmove_clock += 1

    def switch_turn(self) -> None:
        """Переключить очередь хода между белыми и чёрными."""
        self.current_turn = "black" if self.current_turn == "white" else "white"

    def reset_halfmove_clock(self) -> None:
        """Сбросить счётчик полуходов (обычно при взятии или ходе пешки)."""
        self.halfmove_clock = 0

    def is_draw_by_fifty_moves(self) -> bool:
        """Проверить ничью по правилу 50 ходов.

        В правилах FIDE используется 50 ходов без взятия и без хода пешкой,
        что соответствует 100 полуходам.

        Returns:
            bool: True, если halfmove_clock достиг порога.
        """
        return self.halfmove_clock >= 100

    def update_castling_rights(self, piece: str, from_pos: tuple[int, int]) -> None:
        """Обновить права на рокировку после хода короля или ладьи.

        Args:
            piece: Символ фигуры, которая сделала ход.
            from_pos: Координаты начальной клетки (row, col).

        Returns:
            None
        """
        if piece.lower() == "k":
            color = "white" if piece.isupper() else "black"
            self.castling_rights[color]["kingside"] = False
            self.castling_rights[color]["queenside"] = False
        elif piece.lower() == "r":
            color = "white" if piece.isupper() else "black"
            if from_pos[1] == 0:
                self.castling_rights[color]["queenside"] = False
            elif from_pos[1] == 7:
                self.castling_rights[color]["kingside"] = False

    def set_en_passant_target(self, target: tuple[int, int] | None) -> None:
        """Установить клетку для потенциального взятия на проходе.

        Args:
            target: Координаты клетки (row, col) либо None.

        Returns:
            None
        """
        self.en_passant_target = target

    def get_fen(self) -> str:
        """Сформировать строку FEN для текущего состояния (упрощённо).

        Returns:
            str: FEN-строка (в данной реализации — шаблонная доска + параметры).
        """
        return (
            f"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR {self.current_turn[0]} "
            f"KQkq - {self.halfmove_clock} {self.move_count}"
        )

    def set_result(self, result: str) -> None:
        """Установить результат партии.

        Args:
            result: Строка результата (например, "1-0", "0-1", "1/2-1/2").

        Returns:
            None
        """
        self.game_result = result

    def get_last_move(self) -> str | None:
        """Получить последний записанный ход.

        Returns:
            str | None: Последний ход, либо None если история пуста.
        """
        return self.move_history[-1] if self.move_history else None

    def undo_last_move(self) -> str | None:
        """Удалить последний ход из истории и вернуть его.

        Returns:
            str | None: Удалённый ход или None.
        """
        if self.move_history:
            return self.move_history.pop()
        return None
