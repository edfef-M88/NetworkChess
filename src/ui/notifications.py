"""Служебные уведомления приложения."""

from datetime import datetime
from typing import List, Optional, Callable
from enum import Enum

class NotificationType(Enum):
    """Типы уведомлений."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    GAME = "game"

class Notification:
    """Класс уведомления."""

    def __init__(self, message: str, notification_type: NotificationType,
                 duration: int = 3000, action: Optional[Callable] = None):
        self.message = message
        self.type = notification_type
        self.duration = duration
        self.action = action
        self.timestamp = datetime.now()
        self.is_read = False
        self.id = self._generate_id()

    def _generate_id(self) -> str:
        """Генерировать уникальный ID."""
        return f"{self.timestamp.timestamp()}_{hash(self.message)}"

    def mark_as_read(self) -> None:
        """Отметить как прочитанное."""
        self.is_read = True

class NotificationCenter:
    """Центр уведомлений приложения."""

    def __init__(self):
        self.notifications: List[Notification] = []
        self.max_notifications = 50
        self.show_notifications = True
        self.sound_enabled = True
        self.position = "top-right"
        self.callbacks = {}

    def notify(self, message: str, notification_type: str = "info",
              duration: int = 3000, action: Optional[Callable] = None) -> str:
        """Показать уведомление."""
        try:
            ntype = NotificationType(notification_type)
        except ValueError:
            ntype = NotificationType.INFO

        notification = Notification(message, ntype, duration, action)
        self.notifications.append(notification)
        self._trim_notifications()

        if self.show_notifications:
            self._display_notification(notification)

        if self.sound_enabled:
            self._play_notification_sound(ntype)

        return notification.id

    def info(self, message: str, duration: int = 3000) -> str:
        """Информационное уведомление."""
        return self.notify(message, "info", duration)

    def success(self, message: str, duration: int = 3000) -> str:
        """Уведомление об успехе."""
        return self.notify(message, "success", duration)

    def warning(self, message: str, duration: int = 4000) -> str:
        """Предупреждение."""
        return self.notify(message, "warning", duration)

    def error(self, message: str, duration: int = 5000) -> str:
        """Уведомление об ошибке."""
        return self.notify(message, "error", duration)

    def game_event(self, message: str, duration: int = 3000) -> str:
        """Игровое событие."""
        return self.notify(message, "game", duration)

    def notify_game_start(self, white_player: str, black_player: str) -> str:
        """Уведомление о начале игры."""
        message = f"Игра началась: {white_player} (белые) vs {black_player} (черные)"
        return self.game_event(message)

    def notify_game_end(self, result: str, reason: str) -> str:
        """Уведомление об окончании игры."""
        message = f"Игра окончена: {result}. Причина: {reason}"
        return self.game_event(message, duration=5000)

    def notify_check(self, color: str) -> str:
        """Уведомление о шахе."""
        message = f"Шах {'белому' if color == 'white' else 'черному'} королю!"
        return self.warning(message)

    def notify_checkmate(self, winner: str) -> str:
        """Уведомление о мате."""
        message = f"Мат! Победа {winner}!"
        return self.success(message, duration=10000)

    def notify_draw(self, reason: str) -> str:
        """Уведомление о ничьей."""
        message = f"Ничья: {reason}"
        return self.info(message, duration=5000)

    def notify_player_joined(self, player_name: str) -> str:
        """Уведомление о присоединении игрока."""
        message = f"{player_name} присоединился к игре"
        return self.info(message)

    def notify_player_left(self, player_name: str) -> str:
        """Уведомление об уходе игрока."""
        message = f"{player_name} покинул игру"
        return self.warning(message)

    def notify_connection_lost(self) -> str:
        """Уведомление о потере соединения."""
        message = "Соединение с сервером потеряно"
        return self.error(message, duration=10000)

    def notify_connection_restored(self) -> str:
        """Уведомление о восстановлении соединения."""
        message = "Соединение восстановлено"
        return self.success(message)

    def notify_move_invalid(self, reason: str) -> str:
        """Уведомление о недопустимом ходе."""
        message = f"Недопустимый ход: {reason}"
        return self.error(message)

    def notify_time_low(self, player: str, seconds: int) -> str:
        """Уведомление о малом времени."""
        message = f"У {player} осталось {seconds} секунд!"
        return self.warning(message)

    def notify_draw_offer(self, player: str) -> str:
        """Уведомление о предложении ничьей."""
        message = f"{player} предлагает ничью"
        return self.info(message, duration=10000)

    def get_all_notifications(self) -> List[Notification]:
        """Получить все уведомления."""
        return self.notifications.copy()

    def get_unread_notifications(self) -> List[Notification]:
        """Получить непрочитанные уведомления."""
        return [n for n in self.notifications if not n.is_read]

    def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Получить уведомление по ID."""
        for notification in self.notifications:
            if notification.id == notification_id:
                return notification
        return None

    def mark_as_read(self, notification_id: str) -> bool:
        """Отметить уведомление как прочитанное."""
        notification = self.get_notification_by_id(notification_id)
        if notification:
            notification.mark_as_read()
            return True
        return False

    def mark_all_as_read(self) -> None:
        """Отметить все как прочитанные."""
        for notification in self.notifications:
            notification.mark_as_read()

    def clear_notifications(self) -> None:
        """Очистить все уведомления."""
        self.notifications.clear()

    def remove_notification(self, notification_id: str) -> bool:
        """Удалить уведомление."""
        for i, notification in enumerate(self.notifications):
            if notification.id == notification_id:
                self.notifications.pop(i)
                return True
        return False

    def enable_notifications(self) -> None:
        """Включить уведомления."""
        self.show_notifications = True

    def disable_notifications(self) -> None:
        """Отключить уведомления."""
        self.show_notifications = False

    def enable_sound(self) -> None:
        """Включить звук уведомлений."""
        self.sound_enabled = True

    def disable_sound(self) -> None:
        """Отключить звук уведомлений."""
        self.sound_enabled = False

    def set_position(self, position: str) -> bool:
        """Установить позицию уведомлений."""
        valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
        if position in valid_positions:
            self.position = position
            return True
        return False

    def register_callback(self, notification_type: str, callback: Callable) -> None:
        """Зарегистрировать callback для типа уведомлений."""
        self.callbacks[notification_type] = callback

    def _display_notification(self, notification: Notification) -> None:
        """Отобразить уведомление."""
        icon = self._get_icon_for_type(notification.type)
        print(f"{icon} [{notification.type.value.upper()}] {notification.message}")

        # Вызвать callback если есть
        if notification.type.value in self.callbacks:
            self.callbacks[notification.type.value](notification)

    def _play_notification_sound(self, notification_type: NotificationType) -> None:
        """Воспроизвести звук уведомления."""
        # Псевдокод: воспроизвести звук в зависимости от типа
        sounds = {
            NotificationType.INFO: "info.wav",
            NotificationType.SUCCESS: "success.wav",
            NotificationType.WARNING: "warning.wav",
            NotificationType.ERROR: "error.wav",
            NotificationType.GAME: "game.wav"
        }
        sound_file = sounds.get(notification_type, "default.wav")
        # Воспроизвести sound_file

    def _get_icon_for_type(self, notification_type: NotificationType) -> str:
        """Получить иконку для типа уведомления."""
        icons = {
            NotificationType.INFO: "ℹ️",
            NotificationType.SUCCESS: "✅",
            NotificationType.WARNING: "⚠️",
            NotificationType.ERROR: "❌",
            NotificationType.GAME: "♟️"
        }
        return icons.get(notification_type, "📢")

    def _trim_notifications(self) -> None:
        """Обрезать список уведомлений до максимального размера."""
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[-self.max_notifications:]

    def get_notification_count(self) -> dict:
        """Получить количество уведомлений по типам."""
        counts = {
            "total": len(self.notifications),
            "unread": len(self.get_unread_notifications()),
            "info": 0,
            "success": 0,
            "warning": 0,
            "error": 0,
            "game": 0
        }
        for notification in self.notifications:
            counts[notification.type.value] += 1
        return counts

    def export_notifications(self, filename: str) -> bool:
        """Экспортировать уведомления в файл."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for notification in self.notifications:
                    f.write(f"[{notification.timestamp}] [{notification.type.value}] {notification.message}\n")
            return True
        except Exception:
            return False
