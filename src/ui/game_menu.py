"""Игровое меню и навигация по режимам NetworkChess.

Модуль предоставляет класс :class:`GameMenu`, который моделирует главное меню
приложения и операции навигации по пунктам.

Назначение меню в контексте проекта «Сетевые шахматы с уровнями сложности 1–100»:

- предоставить пользователю выбор режима (локально, по сети, против ИИ);
- открыть экраны просмотра повторов, профиля и настроек;
- выдать параметры запуска партии (контроль времени, уровень сложности и т.п.);
- связать UI-выбор пользователя с колбэками/обработчиками.

Текущая реализация является учебной: отрисовка производится в консоль, а
возвращаемые структуры данных являются подготовленными словарями, которые могли
бы быть использованы UI/контроллером для перехода между экранами.
"""

from typing import Optional, Callable, List


class GameMenu:
    """Главное меню приложения NetworkChess.

    Класс хранит список пунктов меню, индекс выбранного пункта и набор
    зарегистрированных callback-функций, которые могут быть вызваны при активации
    конкретного пункта.

    Attributes:
        menu_items: Список пунктов меню (dict с полями id/label/enabled).
        selected_index: Индекс текущего выбранного пункта.
        callbacks: Словарь соответствий menu_id -> callback.
    """

    def __init__(self):
        """Создать меню и заполнить его пунктами по умолчанию.

        Returns:
            None
        """
        self.menu_items = []
        self.selected_index = 0
        self.callbacks = {}
        self._init_menu_items()

    def _init_menu_items(self) -> None:
        """Инициализировать список пунктов меню.

        Returns:
            None
        """
        self.menu_items = [
            {"id": "singleplayer", "label": "Играть с компьютером", "enabled": True},
            {"id": "multiplayer", "label": "Сетевая игра", "enabled": True},
            {"id": "local", "label": "Игра на одном ПК", "enabled": True},
            {"id": "replay", "label": "Просмотр партий", "enabled": True},
            {"id": "profile", "label": "Профиль", "enabled": True},
            {"id": "settings", "label": "Настройки", "enabled": True},
            {"id": "help", "label": "Справка", "enabled": True},
            {"id": "exit", "label": "Выход", "enabled": True},
        ]

    def render(self) -> None:
        """Отрисовать меню в консоль.

        Returns:
            None
        """
        print("=== NetworkChess ===")
        for i, item in enumerate(self.menu_items):
            prefix = "> " if i == self.selected_index else "  "
            status = "" if item["enabled"] else " [Недоступно]"
            print(f"{prefix}{i+1}. {item['label']}{status}")

    def select_next(self) -> None:
        """Переместить выбор на следующий пункт.

        Returns:
            None
        """
        self.selected_index = (self.selected_index + 1) % len(self.menu_items)

    def select_previous(self) -> None:
        """Переместить выбор на предыдущий пункт.

        Returns:
            None
        """
        self.selected_index = (self.selected_index - 1) % len(self.menu_items)

    def select_item(self, index: int) -> bool:
        """Выбрать пункт меню по индексу.

        Args:
            index: Индекс пункта в списке `menu_items` (0..len-1).

        Returns:
            bool: True, если индекс корректен и выбор выполнен.
        """
        if 0 <= index < len(self.menu_items):
            self.selected_index = index
            return True
        return False

    def activate_selected(self) -> Optional[str]:
        """Активировать выбранный пункт меню.

        Метод возвращает идентификатор пункта, если он доступен (enabled=True).
        Внешний код может использовать этот id для переключения экрана или
        выполнения действия.

        Returns:
            Optional[str]: Идентификатор пункта меню или None, если пункт недоступен.
        """
        if 0 <= self.selected_index < len(self.menu_items):
            item = self.menu_items[self.selected_index]
            if item["enabled"]:
                return item["id"]
        return None

    def open_singleplayer(self) -> dict:
        """Сформировать структуру данных для экрана одиночной игры.

        Returns:
            dict: Данные экрана с режимом и списком доступных опций.
        """
        return {"mode": "singleplayer", "options": self._get_singleplayer_options()}

    def open_multiplayer(self) -> dict:
        """Сформировать структуру данных для экрана сетевой игры.

        Returns:
            dict: Данные экрана с режимом и списком доступных опций.
        """
        return {"mode": "multiplayer", "options": self._get_multiplayer_options()}

    def open_local_game(self) -> dict:
        """Сформировать параметры запуска локальной партии на одном ПК.

        Returns:
            dict: Словарь параметров локального режима.
        """
        return {"mode": "local", "players": 2, "time_control": "10+0"}

    def open_replay_browser(self) -> dict:
        """Сформировать данные для экрана просмотра повторов.

        Returns:
            dict: Список доступных повторов (в учебной версии — заглушка).
        """
        return {"mode": "replay", "replays": self._get_available_replays()}

    def open_profile(self) -> dict:
        """Сформировать данные для экрана профиля.

        Returns:
            dict: Данные профиля (учебная заготовка).
        """
        return {"mode": "profile", "username": "Player1", "rating": 1200, "games_played": 0}

    def open_settings(self) -> dict:
        """Сформировать данные для экрана настроек.

        Returns:
            dict: Категории настроек, которые будут показаны пользователю.
        """
        return {"mode": "settings", "categories": ["Графика", "Звук", "Управление", "Сеть"]}

    def open_help(self) -> dict:
        """Сформировать данные для экрана справки.

        Returns:
            dict: Темы справочного раздела.
        """
        return {"mode": "help", "topics": ["Правила", "Управление", "Сетевая игра", "О программе"]}

    def _get_singleplayer_options(self) -> dict:
        """Получить опции режима игры против ИИ.

        Опции включают выбор уровня сложности (1–100 через пресеты), выбор цвета
        и контроль времени.

        Returns:
            dict: Структура настроек одиночного режима.
        """
        return {
            "difficulty_levels": [
                {"name": "Новичок", "level": 20},
                {"name": "Легко", "level": 35},
                {"name": "Средне", "level": 50},
                {"name": "Сложно", "level": 70},
                {"name": "Эксперт", "level": 85},
                {"name": "Мастер", "level": 95},
            ],
            "color_choice": ["Белые", "Черные", "Случайно"],
            "time_controls": ["Без ограничений", "5+0", "10+0", "15+10", "30+0"],
        }

    def _get_multiplayer_options(self) -> dict:
        """Получить опции режима сетевой игры.

        Returns:
            dict: Список доступных действий и параметров для сетевого режима.
        """
        return {
            "actions": ["Создать комнату", "Присоединиться к комнате", "Быстрая игра"],
            "time_controls": ["1+0", "3+0", "5+0", "10+0", "15+10", "30+0"],
            "rated": True,
        }

    def _get_available_replays(self) -> List[dict]:
        """Получить список доступных повторов.

        Returns:
            List[dict]: Список метаданных повторов.
        """
        return [
            {"id": "replay_001", "white": "Player1", "black": "AI_Master", "result": "1-0", "date": "2026-03-12"}
        ]

    def register_callback(self, menu_id: str, callback: Callable) -> None:
        """Зарегистрировать callback для пункта меню.

        Args:
            menu_id: Идентификатор пункта меню (значение поля `id`).
            callback: Функция без аргументов, вызываемая при выполнении.

        Returns:
            None
        """
        self.callbacks[menu_id] = callback

    def execute_callback(self, menu_id: str) -> bool:
        """Выполнить callback, привязанный к пункту меню.

        Args:
            menu_id: Идентификатор пункта меню.

        Returns:
            bool: True, если callback найден и вызван.
        """
        if menu_id in self.callbacks:
            self.callbacks[menu_id]()
            return True
        return False

    def enable_item(self, menu_id: str) -> bool:
        """Сделать пункт меню доступным (enabled=True).

        Args:
            menu_id: Идентификатор пункта меню.

        Returns:
            bool: True, если пункт найден и обновлён.
        """
        for item in self.menu_items:
            if item["id"] == menu_id:
                item["enabled"] = True
                return True
        return False

    def disable_item(self, menu_id: str) -> bool:
        """Сделать пункт меню недоступным (enabled=False).

        Args:
            menu_id: Идентификатор пункта меню.

        Returns:
            bool: True, если пункт найден и обновлён.
        """
        for item in self.menu_items:
            if item["id"] == menu_id:
                item["enabled"] = False
                return True
        return False

    def add_custom_item(self, item_id: str, label: str, position: int = -1) -> bool:
        """Добавить пользовательский пункт меню.

        Args:
            item_id: Уникальный идентификатор пункта.
            label: Отображаемое название пункта.
            position: Позиция вставки. Если -1, пункт добавляется в конец.

        Returns:
            bool: True, если пункт добавлен.
        """
        new_item = {"id": item_id, "label": label, "enabled": True}
        if position == -1:
            self.menu_items.append(new_item)
        else:
            self.menu_items.insert(position, new_item)
        return True

    def remove_item(self, menu_id: str) -> bool:
        """Удалить пункт меню.

        Args:
            menu_id: Идентификатор удаляемого пункта.

        Returns:
            bool: True, если пункт найден и удалён.
        """
        for i, item in enumerate(self.menu_items):
            if item["id"] == menu_id:
                self.menu_items.pop(i)
                return True
        return False

    def get_item_by_id(self, menu_id: str) -> Optional[dict]:
        """Получить пункт меню по его идентификатору.

        Args:
            menu_id: Идентификатор пункта.

        Returns:
            Optional[dict]: Словарь пункта меню или None.
        """
        for item in self.menu_items:
            if item["id"] == menu_id:
                return item
        return None

    def show_quick_play_dialog(self) -> dict:
        """Сформировать параметры для диалога «Быстрая игра».

        Returns:
            dict: Значения по умолчанию для быстрого поиска соперника.
        """
        return {"time_control": "10+0", "color": "random", "rating_range": [1100, 1300]}

    def show_create_room_dialog(self) -> dict:
        """Сформировать параметры для диалога создания сетевой комнаты.

        Returns:
            dict: Структура с полями комнаты (имя, пароль, контроль времени и т.д.).
        """
        return {
            "room_name": "Новая комната",
            "password": "",
            "time_control": "10+0",
            "rated": True,
            "allow_spectators": True,
        }

    def show_join_room_dialog(self) -> dict:
        """Сформировать параметры для диалога подключения к комнате.

        Returns:
            dict: Список доступных комнат (учебная заготовка).
        """
        return {
            "available_rooms": [
                {"id": "room1", "name": "Комната 1", "players": "1/2"},
                {"id": "room2", "name": "Комната 2", "players": "1/2"},
            ]
        }

    def get_selected_item(self) -> Optional[dict]:
        """Получить текущий выбранный пункт меню.

        Returns:
            Optional[dict]: Текущий пункт меню или None.
        """
        if 0 <= self.selected_index < len(self.menu_items):
            return self.menu_items[self.selected_index]
        return None
