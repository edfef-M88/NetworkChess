"""Служебные уведомления приложения."""

class NotificationCenter:
    def notify(self, message: str) -> None:
        print(f"[INFO] {message}")
