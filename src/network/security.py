"""Проверка сетевых сообщений и защита состояния партии."""

class SecurityManager:
    def check_packet(self, payload: dict) -> bool:
        return "type" in payload
