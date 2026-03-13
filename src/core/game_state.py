"""Хранение текущего состояния партии."""

class GameState:
    """Управление состоянием игры."""

    def __init__(self) -> None:
        self.current_turn = "white"
        self.move_history: list[str] = []
        self.move_count = 0
        self.halfmove_clock = 0
        self.castling_rights = {"white": {"kingside": True, "queenside": True},
                                "black": {"kingside": True, "queenside": True}}
        self.en_passant_target = None
        self.game_result = None

    def add_move(self, move: str) -> None:
        """Добавить ход в историю."""
        self.move_history.append(move)
        self.move_count += 1
        self.halfmove_clock += 1

    def switch_turn(self) -> None:
        """Переключить ход."""
        self.current_turn = "black" if self.current_turn == "white" else "white"

    def reset_halfmove_clock(self) -> None:
        """Сбросить счетчик полуходов (при взятии или ходе пешки)."""
        self.halfmove_clock = 0

    def is_draw_by_fifty_moves(self) -> bool:
        """Проверка ничьи по правилу 50 ходов."""
        return self.halfmove_clock >= 100

    def update_castling_rights(self, piece: str, from_pos: tuple[int, int]) -> None:
        """Обновить права на рокировку."""
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
        """Установить клетку для взятия на проходе."""
        self.en_passant_target = target

    def get_fen(self) -> str:
        """Получить FEN-нотацию текущей позиции."""
        return f"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR {self.current_turn[0]} KQkq - {self.halfmove_clock} {self.move_count}"

    def set_result(self, result: str) -> None:
        """Установить результат партии: 1-0, 0-1, 1/2-1/2."""
        self.game_result = result

    def get_last_move(self) -> str | None:
        """Получить последний ход."""
        return self.move_history[-1] if self.move_history else None

    def undo_last_move(self) -> str | None:
        """Отменить последний ход."""
        if self.move_history:
            return self.move_history.pop()
        return None
