"""Клиент сетевой партии."""

import socket
import json
from typing import Callable

class GameClient:
    """Клиент для подключения к сетевой игре."""

    def __init__(self):
        self.socket = None
        self.connected = False
        self.server_address = None
        self.player_id = None
        self.room_id = None
        self.message_handlers = {}

    def connect(self, address: str, port: int = 5555) -> tuple[bool, str]:
        """Подключиться к серверу."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((address, port))
            self.server_address = (address, port)
            self.connected = True
            return True, f"Подключено к {address}:{port}"
        except Exception as e:
            return False, f"Ошибка подключения: {e}"

    def disconnect(self) -> None:
        """Отключиться от сервера."""
        if self.socket:
            self.send_message({"type": "disconnect", "player_id": self.player_id})
            self.socket.close()
            self.connected = False

    def send_message(self, message: dict) -> bool:
        """Отправить сообщение серверу."""
        if not self.connected:
            return False
        try:
            data = json.dumps(message).encode('utf-8')
            self.socket.sendall(data)
            return True
        except Exception:
            return False

    def receive_message(self) -> dict | None:
        """Получить сообщение от сервера."""
        if not self.connected:
            return None
        try:
            data = self.socket.recv(4096)
            if data:
                return json.loads(data.decode('utf-8'))
            return None
        except Exception:
            return None

    def join_room(self, room_id: str, player_name: str) -> tuple[bool, str]:
        """Присоединиться к комнате."""
        message = {
            "type": "join_room",
            "room_id": room_id,
            "player_name": player_name
        }
        if self.send_message(message):
            response = self.receive_message()
            if response and response.get("status") == "success":
                self.room_id = room_id
                self.player_id = response.get("player_id")
                return True, "Успешно присоединились к комнате"
            return False, response.get("error", "Неизвестная ошибка")
        return False, "Не удалось отправить запрос"

    def leave_room(self) -> bool:
        """Покинуть комнату."""
        message = {
            "type": "leave_room",
            "room_id": self.room_id,
            "player_id": self.player_id
        }
        success = self.send_message(message)
        if success:
            self.room_id = None
        return success

    def send_move(self, from_pos: str, to_pos: str) -> bool:
        """Отправить ход."""
        message = {
            "type": "move",
            "room_id": self.room_id,
            "player_id": self.player_id,
            "from": from_pos,
            "to": to_pos
        }
        return self.send_message(message)

    def send_chat_message(self, text: str) -> bool:
        """Отправить сообщение в чат."""
        message = {
            "type": "chat",
            "room_id": self.room_id,
            "player_id": self.player_id,
            "text": text
        }
        return self.send_message(message)

    def request_draw(self) -> bool:
        """Предложить ничью."""
        message = {
            "type": "draw_offer",
            "room_id": self.room_id,
            "player_id": self.player_id
        }
        return self.send_message(message)

    def resign(self) -> bool:
        """Сдаться."""
        message = {
            "type": "resign",
            "room_id": self.room_id,
            "player_id": self.player_id
        }
        return self.send_message(message)

    def register_handler(self, message_type: str, handler: Callable) -> None:
        """Зарегистрировать обработчик для типа сообщений."""
        self.message_handlers[message_type] = handler

    def process_messages(self) -> None:
        """Обработать входящие сообщения."""
        while self.connected:
            message = self.receive_message()
            if message:
                msg_type = message.get("type")
                if msg_type in self.message_handlers:
                    self.message_handlers[msg_type](message)

    def get_room_list(self) -> list[dict]:
        """Получить список доступных комнат."""
        message = {"type": "get_rooms"}
        if self.send_message(message):
            response = self.receive_message()
            return response.get("rooms", [])
        return []

    def ping(self) -> bool:
        """Проверить соединение."""
        message = {"type": "ping"}
        return self.send_message(message)
