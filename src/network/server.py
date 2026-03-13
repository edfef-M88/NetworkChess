"""Сервер координации сетевых партий.

Модуль реализует простой TCP-сервер, который принимает клиентов, создаёт
комнаты (до 2 игроков) и ретранслирует игровые события участникам комнаты:
ходы, сообщения чата, предложения ничьей, сдача, а также служебные запросы
(например, получение списка комнат).

Архитектурно сервер выступает координатором обмена сообщениями и не выполняет
строгую проверку шахматных правил.

Classes:
    MatchServer: Сервер сетевой игры и комнат.
"""

import socket
import json
import threading
from typing import Dict


class MatchServer:
    """Сервер для координации сетевых партий.

    Attributes:
        host: Адрес биндинга.
        port: TCP-порт.
        socket: Сокет прослушивания.
        running: Флаг, указывающий на активную работу сервера.
        rooms: Словарь комнат room_id -> dict.
        clients: Словарь подключённых клиентов player_id -> socket.
        player_rooms: Соответствие игрока и его текущей комнаты.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 5555):
        """Создать сервер.

        Args:
            host: Адрес, на котором будет слушать сервер.
            port: Порт сервера.
        """
        self.host = host
        self.port = port
        self.socket = None
        self.running = False
        self.rooms: Dict[str, dict] = {}
        self.clients: Dict[str, socket.socket] = {}
        self.player_rooms: Dict[str, str] = {}

    def start(self) -> bool:
        """Запустить сервер.

        Returns:
            bool: True при успешном запуске.
        """
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
            self.running = True
            threading.Thread(target=self._accept_connections, daemon=True).start()
            return True
        except Exception:
            return False

    def stop(self) -> None:
        """Остановить сервер и закрыть все соединения."""
        self.running = False
        if self.socket:
            self.socket.close()
        for client_socket in self.clients.values():
            client_socket.close()

    def _accept_connections(self) -> None:
        """Принимать входящие подключения."""
        while self.running:
            try:
                client_socket, _address = self.socket.accept()
                player_id = self._generate_player_id()
                self.clients[player_id] = client_socket
                threading.Thread(
                    target=self._handle_client,
                    args=(player_id, client_socket),
                    daemon=True,
                ).start()
            except Exception:
                break

    def _handle_client(self, player_id: str, client_socket: socket.socket) -> None:
        """Получать сообщения от клиента и передавать их в обработчик.

        Args:
            player_id: ID подключившегося игрока.
            client_socket: Сокет клиента.
        """
        while self.running:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break
                message = json.loads(data.decode("utf-8"))
                self._process_message(player_id, message)
            except Exception:
                break
        self._disconnect_client(player_id)

    def _process_message(self, player_id: str, message: dict) -> None:
        """Маршрутизировать сообщение по типу.

        Args:
            player_id: Отправитель.
            message: Сообщение (dict).
        """
        msg_type = message.get("type")
        if msg_type == "join_room":
            self._handle_join_room(player_id, message)
        elif msg_type == "leave_room":
            self._handle_leave_room(player_id, message)
        elif msg_type == "move":
            self._handle_move(player_id, message)
        elif msg_type == "chat":
            self._handle_chat(player_id, message)
        elif msg_type == "draw_offer":
            self._handle_draw_offer(player_id, message)
        elif msg_type == "resign":
            self._handle_resign(player_id, message)
        elif msg_type == "get_rooms":
            self._handle_get_rooms(player_id)
        elif msg_type == "ping":
            self._send_to_client(player_id, {"type": "pong"})

    def create_room(self, room_name: str, time_control: str = "10+0") -> dict:
        """Создать комнату.

        Args:
            room_name: Название комнаты.
            time_control: Контроль времени.

        Returns:
            dict: Ответ с room_id и статусом.
        """
        room_id = self._generate_room_id()
        self.rooms[room_id] = {
            "id": room_id,
            "name": room_name,
            "status": "waiting",
            "players": [],
            "time_control": time_control,
            "game_state": None,
        }
        return {"room_id": room_id, "status": "created"}

    def _handle_join_room(self, player_id: str, message: dict) -> None:
        """Обработать присоединение игрока к комнате."""
        room_id = message.get("room_id")
        player_name = message.get("player_name")

        if room_id not in self.rooms:
            self._send_to_client(player_id, {"status": "error", "error": "Комната не найдена"})
            return

        room = self.rooms[room_id]
        if len(room["players"]) >= 2:
            self._send_to_client(player_id, {"status": "error", "error": "Комната заполнена"})
            return

        room["players"].append({"id": player_id, "name": player_name})
        self.player_rooms[player_id] = room_id

        self._send_to_client(player_id, {"status": "success", "player_id": player_id, "room": room})

        if len(room["players"]) == 2:
            room["status"] = "playing"
            self._broadcast_to_room(room_id, {"type": "game_start", "players": room["players"]})

    def _handle_leave_room(self, player_id: str, _message: dict) -> None:
        """Обработать выход игрока из комнаты."""
        room_id = self.player_rooms.get(player_id)
        if room_id and room_id in self.rooms:
            room = self.rooms[room_id]
            room["players"] = [p for p in room["players"] if p["id"] != player_id]
            del self.player_rooms[player_id]

            if not room["players"]:
                del self.rooms[room_id]
            else:
                self._broadcast_to_room(room_id, {"type": "player_left", "player_id": player_id})

    def _handle_move(self, player_id: str, message: dict) -> None:
        """Обработать ход (ретрансляция)."""
        room_id = message.get("room_id")
        if room_id in self.rooms:
            self._broadcast_to_room(
                room_id,
                {"type": "move", "player_id": player_id, "from": message.get("from"), "to": message.get("to")},
            )

    def _handle_chat(self, player_id: str, message: dict) -> None:
        """Обработать сообщение чата (ретрансляция)."""
        room_id = message.get("room_id")
        if room_id in self.rooms:
            self._broadcast_to_room(room_id, {"type": "chat", "player_id": player_id, "text": message.get("text")})

    def _handle_draw_offer(self, player_id: str, message: dict) -> None:
        """Обработать предложение ничьей (ретрансляция сопернику)."""
        room_id = message.get("room_id")
        if room_id in self.rooms:
            self._broadcast_to_room(room_id, {"type": "draw_offer", "player_id": player_id}, exclude=player_id)

    def _handle_resign(self, player_id: str, message: dict) -> None:
        """Обработать сдачу и уведомить участников о завершении партии."""
        room_id = message.get("room_id")
        if room_id in self.rooms:
            self._broadcast_to_room(
                room_id,
                {"type": "game_end", "reason": "resign", "winner": self._get_opponent(room_id, player_id)},
            )

    def _handle_get_rooms(self, player_id: str) -> None:
        """Отправить список комнат конкретному клиенту."""
        rooms_list = [
            {"id": r["id"], "name": r["name"], "status": r["status"], "players": len(r["players"])}
            for r in self.rooms.values()
        ]
        self._send_to_client(player_id, {"type": "rooms_list", "rooms": rooms_list})

    def _broadcast_to_room(self, room_id: str, message: dict, exclude: str = None) -> None:
        """Отправить сообщение всем участникам комнаты."""
        if room_id in self.rooms:
            for player in self.rooms[room_id]["players"]:
                if player["id"] != exclude:
                    self._send_to_client(player["id"], message)

    def _send_to_client(self, player_id: str, message: dict) -> bool:
        """Отправить сообщение конкретному клиенту.

        Returns:
            bool: True при успешной отправке.
        """
        if player_id in self.clients:
            try:
                data = json.dumps(message).encode("utf-8")
                self.clients[player_id].sendall(data)
                return True
            except Exception:
                return False
        return False

    def _disconnect_client(self, player_id: str) -> None:
        """Отключить клиента и обновить состояние комнат."""
        if player_id in self.clients:
            self.clients[player_id].close()
            del self.clients[player_id]
        self._handle_leave_room(player_id, {})

    def _generate_player_id(self) -> str:
        """Сгенерировать ID игрока."""
        import uuid

        return str(uuid.uuid4())

    def _generate_room_id(self) -> str:
        """Сгенерировать ID комнаты."""
        import uuid

        return str(uuid.uuid4())[:8]

    def _get_opponent(self, room_id: str, player_id: str) -> str:
        """Получить ID оппонента в комнате.

        Returns:
            str: ID оппонента или None.
        """
        if room_id in self.rooms:
            for player in self.rooms[room_id]["players"]:
                if player["id"] != player_id:
                    return player["id"]
        return None
