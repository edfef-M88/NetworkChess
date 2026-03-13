"""Чат участников партии.

Модуль содержит простую реализацию чата: отправка сообщений игроками,
системные сообщения, ограничение длины сообщений и размера истории, а также
операции модерации (mute/unmute) в рамках конкретного матча.

Classes:
    MatchChat: Хранилище сообщений и операции чата.
"""

from datetime import datetime
from typing import List, Dict


class MatchChat:
    """Управление чатом в игре.

    Attributes:
        messages: История сообщений (каждое сообщение — словарь).
        max_message_length: Максимальная длина текста сообщения.
        max_history: Максимальный размер истории.
        muted_users: Набор идентификаторов пользователей в муте.
        chat_enabled: Флаг включённости чата.
    """

    def __init__(self):
        """Создать чат с пустой историей."""
        self.messages: List[Dict] = []
        self.max_message_length = 500
        self.max_history = 100
        self.muted_users = set()
        self.chat_enabled = True

    def send_message(self, sender_id: str, sender_name: str, text: str) -> tuple[bool, str]:
        """Отправить сообщение в чат.

        Args:
            sender_id: Идентификатор отправителя.
            sender_name: Отображаемое имя.
            text: Текст сообщения.

        Returns:
            tuple[bool, str]: (успех, текст или причина отказа).
        """
        if not self.chat_enabled:
            return False, "Чат отключен"

        if sender_id in self.muted_users:
            return False, "Вы заглушены"

        text = text.strip()
        if not text:
            return False, "Пустое сообщение"

        if len(text) > self.max_message_length:
            text = text[: self.max_message_length]

        message = {
            "sender_id": sender_id,
            "sender_name": sender_name,
            "text": text,
            "timestamp": datetime.now().isoformat(),
            "type": "message",
        }

        self.messages.append(message)
        self._trim_history()
        return True, text

    def send_system_message(self, text: str) -> None:
        """Отправить системное сообщение."""
        message = {
            "sender_id": "system",
            "sender_name": "Система",
            "text": text,
            "timestamp": datetime.now().isoformat(),
            "type": "system",
        }
        self.messages.append(message)
        self._trim_history()

    def send_emote(self, sender_id: str, sender_name: str, emote: str) -> bool:
        """Отправить реакцию (emote) в чат.

        Args:
            sender_id: Идентификатор отправителя.
            sender_name: Имя.
            emote: Код реакции.

        Returns:
            bool: True, если реакция допустима и добавлена.
        """
        valid_emotes = ["wave", "smile", "think", "gg", "glhf"]
        if emote not in valid_emotes:
            return False

        message = {
            "sender_id": sender_id,
            "sender_name": sender_name,
            "emote": emote,
            "timestamp": datetime.now().isoformat(),
            "type": "emote",
        }
        self.messages.append(message)
        return True

    def get_messages(self, limit: int = 50) -> List[Dict]:
        """Получить последние сообщения.

        Args:
            limit: Максимальное количество.

        Returns:
            List[Dict]: Список сообщений.
        """
        return self.messages[-limit:]

    def get_messages_since(self, timestamp: str) -> List[Dict]:
        """Получить сообщения после определённого времени."""
        return [msg for msg in self.messages if msg["timestamp"] > timestamp]

    def clear_history(self) -> None:
        """Очистить историю чата."""
        self.messages.clear()

    def mute_user(self, user_id: str) -> bool:
        """Заглушить пользователя."""
        if user_id not in self.muted_users:
            self.muted_users.add(user_id)
            return True
        return False

    def unmute_user(self, user_id: str) -> bool:
        """Снять заглушение."""
        if user_id in self.muted_users:
            self.muted_users.remove(user_id)
            return True
        return False

    def is_muted(self, user_id: str) -> bool:
        """Проверить, заглушен ли пользователь."""
        return user_id in self.muted_users

    def enable_chat(self) -> None:
        """Включить чат."""
        self.chat_enabled = True
        self.send_system_message("Чат включен")

    def disable_chat(self) -> None:
        """Отключить чат."""
        self.chat_enabled = False
        self.send_system_message("Чат отключен")

    def _trim_history(self) -> None:
        """Обрезать историю до max_history."""
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history :]

    def filter_profanity(self, text: str) -> str:
        """Простейший фильтр нецензурной лексики (заглушка)."""
        bad_words = ["badword1", "badword2"]
        for word in bad_words:
            text = text.replace(word, "***")
        return text

    def get_user_message_count(self, user_id: str) -> int:
        """Получить количество сообщений пользователя."""
        return sum(1 for msg in self.messages if msg.get("sender_id") == user_id)

    def delete_message(self, timestamp: str) -> bool:
        """Удалить сообщение по времени."""
        original_length = len(self.messages)
        self.messages = [msg for msg in self.messages if msg["timestamp"] != timestamp]
        return len(self.messages) < original_length

    def export_chat_log(self) -> str:
        """Экспортировать лог чата."""
        log = "=== Chat Log ===\n"
        for msg in self.messages:
            if msg["type"] == "message":
                log += f"[{msg['timestamp']}] {msg['sender_name']}: {msg['text']}\n"
            elif msg["type"] == "system":
                log += f"[{msg['timestamp']}] SYSTEM: {msg['text']}\n"
            elif msg["type"] == "emote":
                log += f"[{msg['timestamp']}] {msg['sender_name']} {msg['emote']}\n"
        return log
