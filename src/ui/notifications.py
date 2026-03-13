"""Служебные уведомления приложения NetworkChess.

Модуль реализует упрощённую подсистему уведомлений, которая может использоваться
в UI для информирования пользователя о событиях партии и состоянии приложения:

- сетевые события (подключение/потеря соединения, вход/выход игрока);
- игровые события (шах, мат, ничья, начало/окончание партии);
- системные сообщения (ошибки, предупреждения, подтверждения).

В учебной версии уведомления выводятся в консоль, однако интерфейс классов
спроектирован так, чтобы его можно было заменить реальным GUI-компонентом.
"""

from datetime import datetime
from typing import List, Optional, Callable
from enum import Enum


class NotificationType(Enum):
    """Перечень типов уведомлений.

    Значение перечисления используется для унификации отображения и маршрутизации
    уведомлений в :class:`NotificationCenter` (иконки, звук, цвет и т.п.).

    Attributes:
        INFO: Информационное сообщение.
        SUCCESS: Уведомление об успешном действии.
        WARNING: Предупреждение о потенциальной проблеме.
        ERROR: Ошибка или критическая ситуация.
        GAME: Событие, относящееся к партии (шах/мат/результат и т.п.).
    """

    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    GAME = "game"


class Notification:
    """Модель единичного уведомления.

    Объект содержит текст, тип уведомления, служебные метаданные (время создания,
    прочитано/нет) и опциональное действие (callback), которое может быть
    привязано к интерактивному уведомлению.

    Attributes:
        message: Текст уведомления.
        type: Тип уведомления (NotificationType).
        duration: Длительность показа (мс) — актуально для GUI.
        action: Опциональная функция, вызываемая при взаимодействии пользователя.
        timestamp: Время создания уведомления.
        is_read: Признак прочитанного уведомления.
        id: Стабильный идентификатор уведомления внутри текущего запуска.
    """

    def __init__(
        self,
        message: str,
        notification_type: NotificationType,
        duration: int = 3000,
        action: Optional[Callable] = None,
    ):
        """Создать уведомление.

        Args:
            message: Человекочитаемый текст.
            notification_type: Тип уведомления.
            duration: Рекомендуемая длительность отображения (мс).
            action: Функция, связанная с уведомлением (например, открыть экран).

        Returns:
            None
        """
        self.message = message
        self.type = notification_type
        self.duration = duration
        self.action = action
        self.timestamp = datetime.now()
        self.is_read = False
        self.id = self._generate_id()

    def _generate_id(self) -> str:
        """Сгенерировать идентификатор уведомления.

        Идентификатор используется для поиска/удаления уведомления и строится на
        основе времени и содержимого сообщения.

        Returns:
            str: Строковый идентификатор.
        """
        return f"{self.timestamp.timestamp()}_{hash(self.message)}"

    def mark_as_read(self) -> None:
        """Отметить уведомление как прочитанное.

        Returns:
            None
        """
        self.is_read = True


class NotificationCenter:
    """Центр уведомлений приложения.

    Класс накапливает уведомления, предоставляет удобные методы для типовых
    сообщений и реализует минимальную «политику хранения» (обрезка истории).

    Attributes:
        notifications: Список всех уведомлений текущей сессии.
        max_notifications: Максимальное количество уведомлений в памяти.
        show_notifications: Отображать ли уведомления пользователю.
        sound_enabled: Воспроизводить ли звуки уведомлений.
        position: Позиция области уведомлений (для GUI), например "top-right".
        callbacks: Словарь callback-обработчиков по типу уведомления.
    """

    def __init__(self):
        """Создать центр уведомлений с настройками по умолчанию.

        Returns:
            None
        """
        self.notifications: List[Notification] = []
        self.max_notifications = 50
        self.show_notifications = True
        self.sound_enabled = True
        self.position = "top-right"
        self.callbacks = {}

    def notify(
        self,
        message: str,
        notification_type: str = "info",
        duration: int = 3000,
        action: Optional[Callable] = None,
    ) -> str:
        """Создать и показать уведомление.

        Args:
            message: Текст уведомления.
            notification_type: Тип уведомления строкой (должен соответствовать
                элементу NotificationType).
            duration: Длительность показа.
            action: Опциональное действие при клике/выборе.

        Returns:
            str: Идентификатор созданного уведомления.

        Raises:
            ValueError: Может возникнуть при создании NotificationType из строки
                (в данном методе перехватывается и нормализуется до INFO).
        """
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
        """Показать информационное уведомление.

        Args:
            message: Текст уведомления.
            duration: Длительность показа.

        Returns:
            str: ID уведомления.
        """
        return self.notify(message, "info", duration)

    def success(self, message: str, duration: int = 3000) -> str:
        """Показать уведомление об успешном действии.

        Args:
            message: Текст уведомления.
            duration: Длительность показа.

        Returns:
            str: ID уведомления.
        """
        return self.notify(message, "success", duration)

    def warning(self, message: str, duration: int = 4000) -> str:
        """Показать предупреждение пользователю.

        Args:
            message: Текст уведомления.
            duration: Длительность показа.

        Returns:
            str: ID уведомления.
        """
        return self.notify(message, "warning", duration)

    def error(self, message: str, duration: int = 5000) -> str:
        """Показать сообщение об ошибке.

        Args:
            message: Текст уведомления.
            duration: Длительность показа.

        Returns:
            str: ID уведомления.
        """
        return self.notify(message, "error", duration)

    def game_event(self, message: str, duration: int = 3000) -> str:
        """Показать уведомление о событии партии.

        Args:
            message: Текст игрового события.
            duration: Длительность показа.

        Returns:
            str: ID уведомления.
        """
        return self.notify(message, "game", duration)

    def notify_game_start(self, white_player: str, black_player: str) -> str:
        """Сформировать уведомление о начале партии.

        Args:
            white_player: Имя игрока, играющего белыми.
            black_player: Имя игрока, играющего чёрными.

        Returns:
            str: ID уведомления.
        """
        message = f"Игра началась: {white_player} (белые) vs {black_player} (черные)"
        return self.game_event(message)

    def notify_game_end(self, result: str, reason: str) -> str:
        """Сформировать уведомление об окончании партии.

        Args:
            result: Строка результата (например, "1-0" или "1/2-1/2").
            reason: Причина завершения (мат/сдача/ничья и т.п.).

        Returns:
            str: ID уведомления.
        """
        message = f"Игра окончена: {result}. Причина: {reason}"
        return self.game_event(message, duration=5000)

    def notify_check(self, color: str) -> str:
        """Сформировать уведомление о шахе.

        Args:
            color: Цвет короля, которому объявлен шах ("white"/"black").

        Returns:
            str: ID уведомления.
        """
        message = f"Шах {'белому' if color == 'white' else 'черному'} королю!"
        return self.warning(message)

    def notify_checkmate(self, winner: str) -> str:
        """Сформировать уведомление о мате.

        Args:
            winner: Имя стороны/игрока-победителя.

        Returns:
            str: ID уведомления.
        """
        message = f"Мат! Победа {winner}!"
        return self.success(message, duration=10000)

    def notify_draw(self, reason: str) -> str:
        """Сформировать уведомление о ничьей.

        Args:
            reason: Причина ничьей (пат, соглашение, правило 50 ходов и т.п.).

        Returns:
            str: ID уведомления.
        """
        message = f"Ничья: {reason}"
        return self.info(message, duration=5000)

    def notify_player_joined(self, player_name: str) -> str:
        """Сформировать уведомление о присоединении игрока.

        Args:
            player_name: Имя игрока.

        Returns:
            str: ID уведомления.
        """
        message = f"{player_name} присоединился к игре"
        return self.info(message)

    def notify_player_left(self, player_name: str) -> str:
        """Сформировать уведомление об уходе игрока.

        Args:
            player_name: Имя игрока.

        Returns:
            str: ID уведомления.
        """
        message = f"{player_name} покинул игру"
        return self.warning(message)

    def notify_connection_lost(self) -> str:
        """Сформировать уведомление о потере соединения с сервером.

        Returns:
            str: ID уведомления.
        """
        message = "Соединение с сервером потеряно"
        return self.error(message, duration=10000)

    def notify_connection_restored(self) -> str:
        """Сформировать уведомление о восстановлении соединения.

        Returns:
            str: ID уведомления.
        """
        message = "Соединение восстановлено"
        return self.success(message)

    def notify_move_invalid(self, reason: str) -> str:
        """Сформировать уведомление о недопустимом ходе.

        Args:
            reason: Человекочитаемое объяснение причины отказа.

        Returns:
            str: ID уведомления.
        """
        message = f"Недопустимый ход: {reason}"
        return self.error(message)

    def notify_time_low(self, player: str, seconds: int) -> str:
        """Сформировать предупреждение о малом количестве времени на часах.

        Args:
            player: Имя игрока/стороны.
            seconds: Оставшееся время в секундах.

        Returns:
            str: ID уведомления.
        """
        message = f"У {player} осталось {seconds} секунд!"
        return self.warning(message)

    def notify_draw_offer(self, player: str) -> str:
        """Сформировать уведомление о предложении ничьей.

        Args:
            player: Игрок, предложивший ничью.

        Returns:
            str: ID уведомления.
        """
        message = f"{player} предлагает ничью"
        return self.info(message, duration=10000)

    def get_all_notifications(self) -> List[Notification]:
        """Получить копию списка всех уведомлений.

        Returns:
            List[Notification]: Копия списка уведомлений.
        """
        return self.notifications.copy()

    def get_unread_notifications(self) -> List[Notification]:
        """Получить список непрочитанных уведомлений.

        Returns:
            List[Notification]: Непрочитанные уведомления.
        """
        return [n for n in self.notifications if not n.is_read]

    def get_notification_by_id(self, notification_id: str) -> Optional[Notification]:
        """Найти уведомление по его идентификатору.

        Args:
            notification_id: ID уведомления.

        Returns:
            Optional[Notification]: Объект уведомления или None.
        """
        for notification in self.notifications:
            if notification.id == notification_id:
                return notification
        return None

    def mark_as_read(self, notification_id: str) -> bool:
        """Отметить конкретное уведомление как прочитанное.

        Args:
            notification_id: ID уведомления.

        Returns:
            bool: True, если уведомление найдено и обновлено.
        """
        notification = self.get_notification_by_id(notification_id)
        if notification:
            notification.mark_as_read()
            return True
        return False

    def mark_all_as_read(self) -> None:
        """Отметить все уведомления как прочитанные.

        Returns:
            None
        """
        for notification in self.notifications:
            notification.mark_as_read()

    def clear_notifications(self) -> None:
        """Удалить все уведомления из текущей истории.

        Returns:
            None
        """
        self.notifications.clear()

    def remove_notification(self, notification_id: str) -> bool:
        """Удалить уведомление по идентификатору.

        Args:
            notification_id: ID уведомления.

        Returns:
            bool: True, если уведомление найдено и удалено.
        """
        for i, notification in enumerate(self.notifications):
            if notification.id == notification_id:
                self.notifications.pop(i)
                return True
        return False

    def enable_notifications(self) -> None:
        """Включить отображение уведомлений.

        Returns:
            None
        """
        self.show_notifications = True

    def disable_notifications(self) -> None:
        """Отключить отображение уведомлений.

        Returns:
            None
        """
        self.show_notifications = False

    def enable_sound(self) -> None:
        """Включить звук уведомлений.

        Returns:
            None
        """
        self.sound_enabled = True

    def disable_sound(self) -> None:
        """Отключить звук уведомлений.

        Returns:
            None
        """
        self.sound_enabled = False

    def set_position(self, position: str) -> bool:
        """Установить позицию области уведомлений.

        Args:
            position: Одна из строк: "top-left", "top-right", "bottom-left",
                "bottom-right", "center".

        Returns:
            bool: True, если позиция поддерживается и установлена.
        """
        valid_positions = ["top-left", "top-right", "bottom-left", "bottom-right", "center"]
        if position in valid_positions:
            self.position = position
            return True
        return False

    def register_callback(self, notification_type: str, callback: Callable) -> None:
        """Зарегистрировать callback для типа уведомлений.

        Callback будет вызван в момент отображения уведомления данного типа.

        Args:
            notification_type: Строковое значение типа (например, "error").
            callback: Функция, принимающая :class:`Notification`.

        Returns:
            None
        """
        self.callbacks[notification_type] = callback

    def _display_notification(self, notification: Notification) -> None:
        """Отобразить уведомление пользователю.

        В учебной версии отображение реализовано через вывод в консоль.

        Args:
            notification: Уведомление для отображения.

        Returns:
            None
        """
        icon = self._get_icon_for_type(notification.type)
        print(f"{icon} [{notification.type.value.upper()}] {notification.message}")

        # Вызвать callback если есть
        if notification.type.value in self.callbacks:
            self.callbacks[notification.type.value](notification)

    def _play_notification_sound(self, notification_type: NotificationType) -> None:
        """Воспроизвести звук уведомления (псевдокод).

        Args:
            notification_type: Тип уведомления.

        Returns:
            None
        """
        # Псевдокод: воспроизвести звук в зависимости от типа
        sounds = {
            NotificationType.INFO: "info.wav",
            NotificationType.SUCCESS: "success.wav",
            NotificationType.WARNING: "warning.wav",
            NotificationType.ERROR: "error.wav",
            NotificationType.GAME: "game.wav",
        }
        _sound_file = sounds.get(notification_type, "default.wav")
        # Воспроизвести sound_file

    def _get_icon_for_type(self, notification_type: NotificationType) -> str:
        """Получить строковую «иконку» для типа уведомления.

        Args:
            notification_type: Тип уведомления.

        Returns:
            str: Символ/строка для отображения (в учебной версии).
        """
        icons = {
            NotificationType.INFO: "ℹ️",
            NotificationType.SUCCESS: "✅",
            NotificationType.WARNING: "⚠️",
            NotificationType.ERROR: "❌",
            NotificationType.GAME: "♟️",
        }
        return icons.get(notification_type, "📢")

    def _trim_notifications(self) -> None:
        """Обрезать список уведомлений до `max_notifications`.

        Returns:
            None
        """
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[-self.max_notifications :]

    def get_notification_count(self) -> dict:
        """Получить количество уведомлений по типам.

        Returns:
            dict: Сводная статистика: всего, непрочитанные и распределение по типам.
        """
        counts = {
            "total": len(self.notifications),
            "unread": len(self.get_unread_notifications()),
            "info": 0,
            "success": 0,
            "warning": 0,
            "error": 0,
            "game": 0,
        }
        for notification in self.notifications:
            counts[notification.type.value] += 1
        return counts

    def export_notifications(self, filename: str) -> bool:
        """Экспортировать историю уведомлений в текстовый файл.

        Args:
            filename: Путь к файлу, в который будет записан экспорт.

        Returns:
            bool: True при успешной записи.
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                for notification in self.notifications:
                    f.write(
                        f"[{notification.timestamp}] [{notification.type.value}] {notification.message}\n"
                    )
            return True
        except Exception:
            return False
