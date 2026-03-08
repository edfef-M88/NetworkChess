"""Сервер координации матчей."""

class MatchServer:
    def create_room(self, room_name: str) -> dict:
        return {"room": room_name, "status": "created"}
