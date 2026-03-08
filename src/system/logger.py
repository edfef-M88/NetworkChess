"""Журналирование и диагностика."""

class AppLogger:
    def write(self, event: str) -> str:
        return f"LOG: {event}"
