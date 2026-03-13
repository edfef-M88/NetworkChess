"""Журналирование (logging) и диагностика приложения.

Модуль реализует обёртку над стандартным модулем :mod:`logging`, которая
настраивает единый логгер приложения и предоставляет удобные методы для записи
типовых событий (ходы, старт/конец партии, сетевые подключения и т.п.).

В учебной версии NetworkChess логирование используется для:

- отладки сетевого протокола и игровой логики;
- формирования диагностических сообщений при ошибках;
- фиксации ключевых действий пользователя (создание партии, ход, выход).

Важно: данный класс не является «безопасным аудит-логом» и не гарантирует
неизменяемость записей; это именно прикладной журнал для разработчика.

Classes:
    AppLogger: Настраивает логгер приложения и предоставляет методы записи.
"""

import logging
import os
from datetime import datetime
from typing import Optional


class AppLogger:
    """Система логирования приложения NetworkChess.

    Экземпляр класса настраивает логгер с двумя обработчиками:

    - запись в файл (по умолчанию logs/app.log);
    - вывод предупреждений/ошибок в консоль.

    Attributes:
        log_file: Путь к файлу лога.
        level: Текущий уровень логирования в числовом виде (константы logging).
        logger: Объект :class:`logging.Logger`, настроенный для приложения.
    """

    def __init__(self, log_file: str = "logs/app.log", level: str = "INFO") -> None:
        """Создать логгер и выполнить его настройку.

        Args:
            log_file: Путь к файлу лога. Если директория отсутствует, она будет
                создана.
            level: Строковое имя уровня (например, "DEBUG", "INFO").

        Returns:
            None
        """
        self.log_file = log_file
        self.level = self._get_level(level)
        self.logger: logging.Logger | None = None
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Настроить внутренний объект :class:`logging.Logger` и обработчики.

        Метод создаёт директорию под файл лога, настраивает форматтер и добавляет
        file/console handlers.

        Returns:
            None
        """
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)

        self.logger = logging.getLogger("NetworkChess")
        self.logger.setLevel(self.level)

        file_handler = logging.FileHandler(self.log_file, encoding="utf-8")
        file_handler.setLevel(self.level)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def write(self, event: str, level: str = "INFO") -> str:
        """Записать событие в лог и вернуть сформированную строку записи.

        Метод выполняет простую маршрутизацию по уровню и вызывает соответствующий
        метод (debug/info/warning/error/critical).

        Args:
            event: Текст события.
            level: Уровень записи ("DEBUG"/"INFO"/"WARNING"/"ERROR"/"CRITICAL").

        Returns:
            str: Строка записи (в формате ISO-даты), полезная для UI/отладки.
        """
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
        """Записать отладочное сообщение.

        Args:
            message: Текст сообщения.

        Returns:
            None
        """
        if self.logger:
            self.logger.debug(message)

    def info(self, message: str) -> None:
        """Записать информационное сообщение.

        Args:
            message: Текст сообщения.

        Returns:
            None
        """
        if self.logger:
            self.logger.info(message)

    def warning(self, message: str) -> None:
        """Записать предупреждение.

        Args:
            message: Текст предупреждения.

        Returns:
            None
        """
        if self.logger:
            self.logger.warning(message)

    def error(self, message: str, exception: Optional[Exception] = None) -> None:
        """Записать сообщение об ошибке (опционально с traceback).

        Args:
            message: Текст ошибки.
            exception: Экземпляр исключения для добавления деталей и traceback.

        Returns:
            None
        """
        if self.logger:
            if exception:
                self.logger.error(f"{message}: {str(exception)}", exc_info=True)
            else:
                self.logger.error(message)

    def critical(self, message: str) -> None:
        """Записать критическую ошибку.

        Args:
            message: Текст сообщения.

        Returns:
            None
        """
        if self.logger:
            self.logger.critical(message)

    def log_game_start(self, game_id: str, white: str, black: str) -> None:
        """Логировать начало партии.

        Args:
            game_id: Идентификатор партии.
            white: Имя/ID игрока за белых.
            black: Имя/ID игрока за чёрных.

        Returns:
            None
        """
        self.info(f"Game started: {game_id} | White: {white} vs Black: {black}")

    def log_game_end(self, game_id: str, result: str, reason: str) -> None:
        """Логировать завершение партии.

        Args:
            game_id: Идентификатор партии.
            result: Результат (например, "1-0", "0-1", "1/2-1/2").
            reason: Причина завершения (мат, сдача, время и т.п.).

        Returns:
            None
        """
        self.info(f"Game ended: {game_id} | Result: {result} | Reason: {reason}")

    def log_move(self, game_id: str, player: str, move: str) -> None:
        """Логировать сделанный ход.

        Args:
            game_id: Идентификатор партии.
            player: Имя/ID игрока, сделавшего ход.
            move: Ход в строковой нотации.

        Returns:
            None
        """
        self.debug(f"Move in {game_id}: {player} played {move}")

    def log_connection(self, player_id: str, action: str, address: str = "") -> None:
        """Логировать сетевое подключение/отключение.

        Args:
            player_id: Имя/ID пользователя.
            action: Действие ("connect" или "disconnect").
            address: Адрес клиента (используется при connect).

        Returns:
            None
        """
        if action == "connect":
            self.info(f"Player {player_id} connected from {address}")
        elif action == "disconnect":
            self.info(f"Player {player_id} disconnected")

    def log_error_with_context(self, error: str, context: dict) -> None:
        """Логировать ошибку вместе с набором контекстных параметров.

        Args:
            error: Сообщение об ошибке.
            context: Словарь контекстных данных (ключ → значение), которые будут
                сериализованы в строку.

        Returns:
            None
        """
        context_str = ", ".join(f"{k}={v}" for k, v in context.items())
        self.error(f"{error} | Context: {context_str}")

    def log_performance(self, operation: str, duration_ms: float) -> None:
        """Логировать метрику производительности для операции.

        Args:
            operation: Имя/описание операции.
            duration_ms: Длительность в миллисекундах.

        Returns:
            None
        """
        if duration_ms > 1000:
            self.warning(f"Slow operation: {operation} took {duration_ms:.2f}ms")
        else:
            self.debug(f"Operation: {operation} took {duration_ms:.2f}ms")

    def log_security_event(self, event_type: str, details: str) -> None:
        """Логировать событие безопасности.

        Метод предназначен для фиксации подозрительных действий (невалидные
        сообщения, превышение лимитов, ошибки подписи и т.п.).

        Args:
            event_type: Тип события (категория).
            details: Детали события.

        Returns:
            None
        """
        self.warning(f"SECURITY: {event_type} - {details}")

    def get_recent_logs(self, lines: int = 100) -> list[str]:
        """Получить последние строки лога из файла.

        Args:
            lines: Сколько строк вернуть с конца файла.

        Returns:
            list[str]: Список строк. Если файл недоступен — пустой список.
        """
        try:
            with open(self.log_file, "r", encoding="utf-8") as f:
                return f.readlines()[-lines:]
        except Exception:
            return []

    def clear_logs(self) -> bool:
        """Очистить файл лога.

        Returns:
            bool: True, если очистка выполнена успешно.
        """
        try:
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write("")
            self.info("Logs cleared")
            return True
        except Exception:
            return False

    def set_level(self, level: str) -> None:
        """Изменить уровень логирования у логгера.

        Args:
            level: Строковое имя уровня (например, "INFO").

        Returns:
            None
        """
        self.level = self._get_level(level)
        if self.logger:
            self.logger.setLevel(self.level)

    def _get_level(self, level: str) -> int:
        """Преобразовать строковое имя уровня в числовую константу logging.

        Args:
            level: Строковое имя уровня.

        Returns:
            int: Значение из :mod:`logging` (например, logging.INFO).
        """
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return levels.get(level.upper(), logging.INFO)

    def export_logs(self, output_file: str) -> bool:
        """Экспортировать файл логов в другое место.

        Args:
            output_file: Путь назначения для копии файла лога.

        Returns:
            bool: True, если копирование прошло успешно.
        """
        try:
            import shutil

            shutil.copy(self.log_file, output_file)
            return True
        except Exception:
            return False
