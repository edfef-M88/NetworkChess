"""Учётные записи и профили пользователей NetworkChess.

Модуль реализует сервис управления пользователями для учебного проекта
«Сетевые шахматы с уровнями сложности 1–100».

Функциональность сервиса включает:

- регистрацию пользователей и хранение профилей;
- аутентификацию по паролю (с хранением хеша пароля);
- управление сессиями (выдача и отзыв токена сессии);
- обновление данных профиля и настройка пользовательских параметров;
- учёт рейтинга и базовой статистики (сыгранные партии/победы/поражения/ничьи).

Важно: реализация ориентирована на лабораторную работу и не является
промышленной системой безопасности. Например, отсутствуют salt для паролей,
политика сложности пароля ограничена, а токены сессий не имеют срока жизни.
"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Optional


class AccountService:
    """Сервис управления учетными записями пользователей.

    Класс предоставляет высокоуровневые операции по работе с аккаунтами:
    регистрация, вход, выход, изменение пароля и обновление профиля. Данные
    хранятся в JSON-файле по пути `storage_path`.

    Attributes:
        storage_path: Путь к JSON-файлу, в котором хранятся аккаунты.
        accounts: Словарь username -> данные аккаунта.
        active_sessions: Словарь session_token -> username для активных сессий.
    """

    def __init__(self, storage_path: str = "data/accounts.json"):
        """Инициализировать сервис аккаунтов.

        Args:
            storage_path: Путь к файлу хранения аккаунтов.

        Returns:
            None
        """
        self.storage_path = storage_path
        self.accounts: Dict[str, dict] = {}
        self.active_sessions: Dict[str, str] = {}
        self.load_accounts()

    def register(self, username: str, password: str, email: str = "") -> dict:
        """Зарегистрировать нового пользователя.

        Метод выполняет базовую валидацию имени пользователя и пароля, создаёт
        запись аккаунта со стартовыми значениями рейтинга/статистики и
        сохраняет обновлённый набор аккаунтов на диск.

        Args:
            username: Логин пользователя (используется как ключ в хранилище).
            password: Пароль в открытом виде (будет захеширован перед записью).
            email: Адрес электронной почты (опционально).

        Returns:
            dict: Результат операции. При успехе содержит статус "created" и имя
            пользователя; при ошибке — статус "error" и сообщение.
        """
        if not self._validate_username(username):
            return {"status": "error", "message": "Неверное имя пользователя"}

        if username in self.accounts:
            return {"status": "error", "message": "Пользователь уже существует"}

        if not self._validate_password(password):
            return {"status": "error", "message": "Слабый пароль"}

        password_hash = self._hash_password(password)
        account = {
            "username": username,
            "password_hash": password_hash,
            "email": email,
            "created_at": datetime.now().isoformat(),
            "rating": 1200,
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "avatar": "default.png",
            "settings": self._default_settings(),
        }

        self.accounts[username] = account
        self.save_accounts()
        return {"status": "created", "username": username}

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """Выполнить вход пользователя и выдать токен сессии.

        Args:
            username: Имя пользователя.
            password: Пароль в открытом виде.

        Returns:
            tuple[bool, str]: (успешно ли, токен сессии или текст ошибки).
        """
        if username not in self.accounts:
            return False, "Пользователь не найден"

        account = self.accounts[username]
        password_hash = self._hash_password(password)

        if password_hash != account["password_hash"]:
            return False, "Неверный пароль"

        session_token = self._generate_session_token(username)
        self.active_sessions[session_token] = username
        return True, session_token

    def logout(self, session_token: str) -> bool:
        """Завершить активную сессию пользователя.

        Args:
            session_token: Токен сессии, выданный при login().

        Returns:
            bool: True, если сессия существовала и была удалена.
        """
        if session_token in self.active_sessions:
            del self.active_sessions[session_token]
            return True
        return False

    def get_profile(self, username: str) -> Optional[dict]:
        """Получить публичный профиль пользователя.

        Возвращаемый профиль не содержит `password_hash`.

        Args:
            username: Имя пользователя.

        Returns:
            Optional[dict]: Копия профиля без чувствительных данных или None.
        """
        if username in self.accounts:
            profile = self.accounts[username].copy()
            profile.pop("password_hash", None)
            return profile
        return None

    def update_profile(self, username: str, updates: dict) -> bool:
        """Обновить допустимые поля профиля пользователя.

        Ограничение набора полей позволяет избежать случайной порчи структуры
        аккаунта.

        Args:
            username: Имя пользователя.
            updates: Словарь изменений.

        Returns:
            bool: True, если профиль обновлён и сохранён.
        """
        if username not in self.accounts:
            return False

        allowed_fields = ["email", "avatar", "settings"]
        for field, value in updates.items():
            if field in allowed_fields:
                self.accounts[username][field] = value

        self.save_accounts()
        return True

    def change_password(self, username: str, old_password: str, new_password: str) -> tuple[bool, str]:
        """Изменить пароль пользователя.

        Args:
            username: Имя пользователя.
            old_password: Текущий пароль.
            new_password: Новый пароль.

        Returns:
            tuple[bool, str]: (успешно ли, сообщение).
        """
        if username not in self.accounts:
            return False, "Пользователь не найден"

        old_hash = self._hash_password(old_password)
        if old_hash != self.accounts[username]["password_hash"]:
            return False, "Неверный старый пароль"

        if not self._validate_password(new_password):
            return False, "Слабый новый пароль"

        new_hash = self._hash_password(new_password)
        self.accounts[username]["password_hash"] = new_hash
        self.save_accounts()
        return True, "Пароль изменен"

    def update_rating(self, username: str, rating_change: int) -> bool:
        """Изменить рейтинг пользователя на указанную величину.

        Args:
            username: Имя пользователя.
            rating_change: Приращение рейтинга (может быть отрицательным).

        Returns:
            bool: True, если пользователь найден и рейтинг обновлён.
        """
        if username in self.accounts:
            self.accounts[username]["rating"] += rating_change
            self.accounts[username]["rating"] = max(0, self.accounts[username]["rating"])
            self.save_accounts()
            return True
        return False

    def record_game_result(self, username: str, result: str) -> bool:
        """Записать результат завершённой партии в профиль пользователя.

        Args:
            username: Имя пользователя.
            result: Один из результатов: "win", "loss", "draw".

        Returns:
            bool: True, если пользователь найден и статистика обновлена.
        """
        if username not in self.accounts:
            return False

        account = self.accounts[username]
        account["games_played"] += 1

        if result == "win":
            account["wins"] += 1
        elif result == "loss":
            account["losses"] += 1
        elif result == "draw":
            account["draws"] += 1

        self.save_accounts()
        return True

    def get_leaderboard(self, limit: int = 10) -> list:
        """Сформировать таблицу лидеров по рейтингу.

        Args:
            limit: Максимальное количество записей в таблице.

        Returns:
            list: Список словарей с краткими данными игроков.
        """
        sorted_accounts = sorted(self.accounts.values(), key=lambda x: x["rating"], reverse=True)
        return [
            {
                "username": acc["username"],
                "rating": acc["rating"],
                "games_played": acc["games_played"],
                "wins": acc["wins"],
            }
            for acc in sorted_accounts[:limit]
        ]

    def delete_account(self, username: str, password: str) -> tuple[bool, str]:
        """Удалить учётную запись пользователя.

        Args:
            username: Имя пользователя.
            password: Пароль для подтверждения операции.

        Returns:
            tuple[bool, str]: (успешно ли, сообщение).
        """
        if username not in self.accounts:
            return False, "Пользователь не найден"

        password_hash = self._hash_password(password)
        if password_hash != self.accounts[username]["password_hash"]:
            return False, "Неверный пароль"

        del self.accounts[username]
        self.save_accounts()
        return True, "Аккаунт удален"

    def _validate_username(self, username: str) -> bool:
        """Проверить корректность имени пользователя.

        В данной реализации допустимы только буквенно-цифровые имена длиной
        3..20 символов.

        Args:
            username: Имя пользователя.

        Returns:
            bool: True, если имя соответствует правилам.
        """
        if len(username) < 3 or len(username) > 20:
            return False
        return username.isalnum()

    def _validate_password(self, password: str) -> bool:
        """Проверить пароль на минимальные требования.

        Args:
            password: Пароль.

        Returns:
            bool: True, если длина пароля удовлетворяет минимальному порогу.
        """
        return len(password) >= 6

    def _hash_password(self, password: str) -> str:
        """Получить хеш пароля.

        Args:
            password: Пароль в открытом виде.

        Returns:
            str: SHA-256 хеш пароля.
        """
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _generate_session_token(self, username: str) -> str:
        """Сгенерировать токен сессии для пользователя.

        Args:
            username: Имя пользователя.

        Returns:
            str: Строковый токен сессии.
        """
        data = f"{username}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def _default_settings(self) -> dict:
        """Сформировать настройки по умолчанию для нового аккаунта.

        Returns:
            dict: Словарь настроек.
        """
        return {"theme": "classic", "sound_enabled": True, "show_legal_moves": True, "auto_queen": False}

    def save_accounts(self) -> bool:
        """Сохранить текущие аккаунты в файл.

        Returns:
            bool: True при успешной записи.

        Raises:
            OSError: Может возникнуть при проблемах с доступом к файлу/папке.
        """
        try:
            with open(self.storage_path, "w") as f:
                json.dump(self.accounts, f, indent=2)
            return True
        except Exception:
            return False

    def load_accounts(self) -> bool:
        """Загрузить аккаунты из файла в память.

        Returns:
            bool: True, если файл успешно прочитан и данные загружены.

        Raises:
            FileNotFoundError: Если файл ещё не создан (перехватывается и
                преобразуется в пустое хранилище).
        """
        try:
            with open(self.storage_path, "r") as f:
                self.accounts = json.load(f)
            return True
        except FileNotFoundError:
            self.accounts = {}
            return False
        except Exception:
            return False
