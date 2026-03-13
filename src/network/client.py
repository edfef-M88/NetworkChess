"""Сетевой клиент для подключения к партии.

Модуль реализует клиентскую часть сетевого взаимодействия: подключение по TCP,
отправка/получение JSON-сообщений, присоединение/выход из комнаты, отправка
ходов и сообщений чата, а также диспетчеризация входящих сообщений по
зарегистрированным обработчикам.

Classes:
    GameClient: Клиент сетевой игры.
"""

import socket
import json
from typing import Callable


class GameClient:
    """Клиент для подключения к сетевой игре.

    Attributes:
        socket: TCP-сокет, используемый для связи с сервером.
        connected: Признак активного соединения.
        server_address: Кортеж (host, port) сервера, либо None.
        player_id: Идентификатор игрока, выданный сервером.
        room_id: Идентификатор текущей комнаты.
        message_handlers: Словарь обработчиков входящих сообщений по типу.
    """

    def __init__(self):
        """Создать клиент в отключённом состоянии."""
        self.socket = None
        self.connected = False
        self.server_address = None
        self.player_id = None
        self.room_id = None
        self.message_handlers = {}

    def connect(self, address: str, port: int = 5555) -> tuple[bool, str]:
        """Подключиться к серверу.

        Args:
            address: IP/hostname сервера.
            port: TCP-порт сервера.

        Returns:
            tuple[bool, str]: (успех, диагностическое сообщение).
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((address, port))
            self.server_address = (address, port)
            self.connected = True
            return True, f"Подключено к {address}:{port}"
        except Exception as e:
            return False, f"Ошибка подключения: {e}"

    def disconnect(self) -> None:
        """Отключиться от сервера и закрыть сокет."""
        if self.socket:
            self.send_message({"type": "disconnect", "player_id": self.player_id})
            self.socket.close()
            self.connected = False

    def send_message(self, message: dict) -> bool:
        """Отправить сообщение серверу.

        Args:
            message: Словарь, который будет сериализован в JSON.

        Returns:
            bool: True при успешной отправке.
        """
        if not self.connected:
            return False
        try:
            data = json.dumps(message).encode("utf-8")
            self.socket.sendall(data)
            return True
        except Exception:
            return False

    def receive_message(self) -> dict | None:
        """Получить сообщение от сервера.

        Returns:
            dict | None: Декодированное JSON-сообщение либо None.
        """
        if not self.connected:
            return None
        try:
            data = self.socket.recv(4096)
            if data:
                return json.loads(data.decode("utf-8"))
            return None
        except Exception:
            return None

    def join_room(self, room_id: str, player_name: str) -> tuple[bool, str]:
        """Присоединиться к комнате.

        Args:
            room_id: Идентификатор комнаты.
            player_name: Имя игрока.

        Returns:
            tuple[bool, str]: (успех, сообщение/ошибка).
        """
        message = {"type": "join_room", "room_id": room_id, "player_name": player_name}
        if self.send_message(message):
            response = self.receive_message()
            if response and response.get("status") == "success":
                self.room_id = room_id
                self.player_id = response.get("player_id")
                return True, "Успешно присоединились к комнате"
            return False, response.get("error", "Неизвестная ошибка")
        return False, "Не удалось отправить запрос"

    def leave_room(self) -> bool:
        """Покинуть текущую комнату.

        Returns:
            bool: True при успешной отправке запроса.
        """
        message = {"type": "leave_room", "room_id": self.room_id, "player_id": self.player_id}
        success = self.send_message(message)
        if success:
            self.room_id = None
        return success

    def send_move(self, from_pos: str, to_pos: str) -> bool:
        """Отправить ход на сервер.

        Args:
            from_pos: Начальная клетка (например, "e2").
            to_pos: Конечная клетка (например, "e4").

        Returns:
            bool: True, если сообщение отправлено.
        """
        message = {
            "type": "move",
            "room_id": self.room_id,
            "player_id": self.player_id,
            "from": from_pos,
            "to": to_pos,
        }
        return self.send_message(message)

    def send_chat_message(self, text: str) -> bool:
        """Отправить сообщение в чат комнаты.

        Args:
            text: Текст сообщения.

        Returns:
            bool: True при успешной отправке.
        """
        message = {
            "type": "chat",
            "room_id": self.room_id,
            "player_id": self.player_id,
            "text": text,
        }
        return self.send_message(message)

    def request_draw(self) -> bool:
        """Предложить ничью сопернику (через сервер).

        Returns:
            bool: True при успешной отправке.
        """
        message = {"type": "draw_offer", "room_id": self.room_id, "player_id": self.player_id}
        return self.send_message(message)

    def resign(self) -> bool:
        """Сдаться (закончить партию поражением).

        Returns:
            bool: True при успешной отправке.
        """
        message = {"type": "resign", "room_id": self.room_id, "player_id": self.player_id}
        return self.send_message(message)

    def register_handler(self, message_type: str, handler: Callable) -> None:
        """Зарегистрировать обработчик входящих сообщений.

        Args:
            message_type: Поле "type" входящего сообщения.
            handler: Вызываемая функция, принимающая dict.

        Returns:
            None
        """
        self.message_handlers[message_type] = handler

    def process_messages(self) -> None:
        """Цикл обработки входящих сообщений.

        Метод читает сообщения из сокета и, если для типа зарегистрирован
        обработчик, вызывает его.

        Returns:
            None
        """
        while self.connected:
            message = self.receive_message()
            if message:
                msg_type = message.get("type")
                if msg_type in self.message_handlers:
                    self.message_handlers[msg_type](message)

    def get_room_list(self) -> list[dict]:
        """Запросить у сервера список доступных комнат.

        Returns:
            list[dict]: Список комнат, полученный от сервера.
        """
        message = {"type": "get_rooms"}
        if self.send_message(message):
            response = self.receive_message()
            return response.get("rooms", [])
        return []

    def ping(self) -> bool:
        """Отправить ping на сервер, чтобы проверить соединение.

        Returns:
            bool: True при успешной отправке.
        """
        message = {"type": "ping"}
        return self.send_message(message)
