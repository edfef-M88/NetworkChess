"""Журналирование и диагностика."""

import logging
from datetime import datetime
from typing import Optional
import os

class AppLogger:
    """Система логирования приложения."""

    def __init__(self, log_file: str = "logs/app.log", level: str = "INFO"):
        self.log_file = log_file
        self.level = self._get_level(level)
        self.logger = None
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Настроить логгер."""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        self.logger = logging.getLogger("NetworkChess")
        self.logger.setLevel(self.level)

        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(self.level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def write(self, event: str, level: str = "INFO") -> str:
        """Записать событие в лог."""
        log_entry = f"[{datetime.now().isoformat()}] {level}: {event}"

        if level == "DEBUG":
            self.debug(event)
        elif level == "INFO":
            self.info(event)
        elif level == "WARNING":
            self.warning(event)
        elif level == "ERROR":
            self.error(event)
        elif level == "CRITICAL":
            self.critical(event)

        return log_entry

    def debug(self, message: str) -> None:
        """Отладочное сообщение."""
        if self.logger:
            self.logger.debug(message)

    def info(self, message: str) -> None:
        """Информационное сообщение."""
        if self.logger:
            self.logger.info(message)

    def warning(self, message: str) -> None:
        """Предупреждение."""
        if self.logger:
            self.logger.warning(message)

    def error(self, message: str, exception: Optional[Exception] = None) -> None:
        """Ошибка."""
        if self.logger:
            if exception:
                self.logger.error(f"{message}: {str(exception)}", exc_info=True)
            else:
                self.logger.error(message)

    def critical(self, message: str) -> None:
        """Критическая ошибка."""
        if self.logger:
            self.logger.critical(message)

    def log_game_start(self, game_id: str, white: str, black: str) -> None:
        """Логировать начало игры."""
        self.info(f"Game started: {game_id} | White: {white} vs Black: {black}")

    def log_game_end(self, game_id: str, result: str, reason: str) -> None:
        """Логировать окончание игры."""
        self.info(f"Game ended: {game_id} | Result: {result} | Reason: {reason}")

    def log_move(self, game_id: str, player: str, move: str) -> None:
        """Логировать ход."""
        self.debug(f"Move in {game_id}: {player} played {move}")

    def log_connection(self, player_id: str, action: str, address: str = "") -> None:
        """Логировать подключение."""
        if action == "connect":
            self.info(f"Player {player_id} connected from {address}")
        elif action == "disconnect":
            self.info(f"Player {player_id} disconnected")

    def log_error_with_context(self, error: str, context: dict) -> None:
        """Логировать ошибку с контекстом."""
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        self.error(f"{error} | Context: {context_str}")

    def log_performance(self, operation: str, duration_ms: float) -> None:
        """Логировать производительность."""
        if duration_ms > 1000:
            self.warning(f"Slow operation: {operation} took {duration_ms:.2f}ms")
        else:
            self.debug(f"Operation: {operation} took {duration_ms:.2f}ms")

    def log_security_event(self, event_type: str, details: str) -> None:
        """Логировать событие безопасности."""
        self.warning(f"SECURITY: {event_type} - {details}")

    def get_recent_logs(self, lines: int = 100) -> list[str]:
        """Получить последние строки лога."""
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return f.readlines()[-lines:]
        except Exception:
            return []

    def clear_logs(self) -> bool:
        """Очистить логи."""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("")
            self.info("Logs cleared")
            return True
        except Exception:
            return False

    def set_level(self, level: str) -> None:
        """Установить уровень логирования."""
        self.level = self._get_level(level)
        if self.logger:
            self.logger.setLevel(self.level)

    def _get_level(self, level: str) -> int:
        """Получить числовой уровень логирования."""
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return levels.get(level.upper(), logging.INFO)

    def export_logs(self, output_file: str) -> bool:
        """Экспортировать логи в файл."""
        try:
            import shutil
            shutil.copy(self.log_file, output_file)
            return True
        except Exception:
            return False
