"""Проверка сетевых сообщений и защита состояния партии.

Модуль содержит набор проверок входящих сообщений сетевой игры:
- базовая проверка наличия типа сообщения;
- примитивный rate-limit по отправителю;
- проверка структуры сообщения по обязательным полям;
- подпись сообщений HMAC (опционально);
- утилиты для упрощённой «санитизации» текста и проверки шахматной нотации.

Важно: код предназначен для учебного проекта и не заменяет полноценные
механизмы защиты (TLS, строгая аутентификация, защита от replay-атак и т.п.).

Classes:
    SecurityManager: Менеджер проверок и подписей сообщений.
"""

import hashlib
import hmac
import time
from typing import Dict, Set


class SecurityManager:
    """Управление безопасностью сетевых сообщений.

    Attributes:
        secret_key: Ключ подписи сообщений (bytes).
        message_history: История подозрительной активности (по sender_id).
        blocked_ips: Набор заблокированных IP.
        rate_limits: Таймстемпы сообщений по отправителю.
        max_messages_per_minute: Максимальное число сообщений в минуту.
    """

    def __init__(self, secret_key: str = "default_secret"):
        """Создать менеджер безопасности.

        Args:
            secret_key: Секретный ключ для HMAC.
        """
        self.secret_key = secret_key.encode("utf-8")
        self.message_history: Dict[str, list] = {}
        self.blocked_ips: Set[str] = set()
        self.rate_limits: Dict[str, list] = {}
        self.max_messages_per_minute = 60

    def check_packet(self, payload: dict) -> bool:
        """Базовая проверка пакета.

        Args:
            payload: Входящее сообщение.

        Returns:
            bool: True, если присутствует ключ "type".
        """
        return "type" in payload

    def validate_message(self, payload: dict, sender_id: str) -> tuple[bool, str]:
        """Полная валидация сообщения.

        Args:
            payload: Сообщение.
            sender_id: Идентификатор отправителя.

        Returns:
            tuple[bool, str]: (валидно ли, сообщение/причина).
        """
        if not self.check_packet(payload):
            return False, "Отсутствует тип сообщения"

        if not self._check_rate_limit(sender_id):
            return False, "Превышен лимит сообщений"

        if not self._validate_message_structure(payload):
            return False, "Неверная структура сообщения"

        if "signature" in payload:
            if not self._verify_signature(payload):
                return False, "Неверная подпись"

        return True, "OK"

    def _check_rate_limit(self, sender_id: str) -> bool:
        """Проверить лимит частоты сообщений (окно 60 секунд)."""
        current_time = time.time()
        if sender_id not in self.rate_limits:
            self.rate_limits[sender_id] = []

        self.rate_limits[sender_id] = [t for t in self.rate_limits[sender_id] if current_time - t < 60]

        if len(self.rate_limits[sender_id]) >= self.max_messages_per_minute:
            return False

        self.rate_limits[sender_id].append(current_time)
        return True

    def _validate_message_structure(self, payload: dict) -> bool:
        """Проверить структуру сообщения по списку обязательных полей."""
        msg_type = payload.get("type")
        required_fields = {
            "move": ["room_id", "player_id", "from", "to"],
            "chat": ["room_id", "player_id", "text"],
            "join_room": ["room_id", "player_name"],
            "draw_offer": ["room_id", "player_id"],
            "resign": ["room_id", "player_id"],
        }

        if msg_type in required_fields:
            for field in required_fields[msg_type]:
                if field not in payload:
                    return False

        return True

    def sign_message(self, message: dict) -> dict:
        """Подписать сообщение HMAC-SHA256.

        Args:
            message: Сообщение без подписи.

        Returns:
            dict: Копия сообщения с полем "signature".
        """
        message_copy = message.copy()
        message_str = str(sorted(message_copy.items()))
        signature = hmac.new(self.secret_key, message_str.encode("utf-8"), hashlib.sha256).hexdigest()
        message_copy["signature"] = signature
        return message_copy

    def _verify_signature(self, message: dict) -> bool:
        """Проверить подпись сообщения."""
        if "signature" not in message:
            return False

        signature = message.pop("signature")
        message_str = str(sorted(message.items()))
        expected_signature = hmac.new(self.secret_key, message_str.encode("utf-8"), hashlib.sha256).hexdigest()

        message["signature"] = signature
        return hmac.compare_digest(signature, expected_signature)

    def sanitize_input(self, text: str) -> str:
        """Очистить пользовательский ввод.

        Ограничивает длину и удаляет набор потенциально опасных символов.

        Args:
            text: Исходный текст.

        Returns:
            str: Очищенный текст.
        """
        text = text.strip()
        text = text[:500]
        forbidden_chars = ["<", ">", "&", '"', "'"]
        for char in forbidden_chars:
            text = text.replace(char, "")
        return text

    def validate_move(self, move_data: dict) -> bool:
        """Валидация данных хода на уровне нотации.

        Args:
            move_data: Сообщение хода.

        Returns:
            bool: True, если поля "from" и "to" выглядят корректно.
        """
        from_pos = move_data.get("from", "")
        to_pos = move_data.get("to", "")

        if not self._is_valid_chess_notation(from_pos):
            return False
        if not self._is_valid_chess_notation(to_pos):
            return False

        return True

    def _is_valid_chess_notation(self, notation: str) -> bool:
        """Проверка шахматной нотации клетки."""
        if len(notation) != 2:
            return False
        if notation[0] not in "abcdefgh":
            return False
        if notation[1] not in "12345678":
            return False
        return True

    def block_ip(self, ip_address: str) -> None:
        """Заблокировать IP адрес."""
        self.blocked_ips.add(ip_address)

    def unblock_ip(self, ip_address: str) -> None:
        """Разблокировать IP адрес."""
        self.blocked_ips.discard(ip_address)

    def is_blocked(self, ip_address: str) -> bool:
        """Проверить, заблокирован ли IP."""
        return ip_address in self.blocked_ips

    def log_suspicious_activity(self, sender_id: str, activity: str) -> None:
        """Записать подозрительную активность."""
        if sender_id not in self.message_history:
            self.message_history[sender_id] = []
        self.message_history[sender_id].append({"activity": activity, "timestamp": time.time()})

    def get_activity_log(self, sender_id: str) -> list:
        """Получить лог активности."""
        return self.message_history.get(sender_id, [])

    def encrypt_data(self, data: str) -> str:
        """Псевдо-«шифрование» данных (хеширование SHA-256)."""
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def validate_session_token(self, token: str, player_id: str) -> bool:
        """Проверить токен сессии."""
        expected_token = self.encrypt_data(f"{player_id}:{self.secret_key.decode()}")
        return token == expected_token
