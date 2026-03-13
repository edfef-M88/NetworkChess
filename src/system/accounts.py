"""Учётные записи и профили пользователей."""

import hashlib
import json
from datetime import datetime
from typing import Dict, Optional

class AccountService:
    """Управление учетными записями пользователей."""

    def __init__(self, storage_path: str = "data/accounts.json"):
        self.storage_path = storage_path
        self.accounts: Dict[str, dict] = {}
        self.active_sessions: Dict[str, str] = {}
        self.load_accounts()

    def register(self, username: str, password: str, email: str = "") -> dict:
        """Регистрация нового пользователя."""
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
            "settings": self._default_settings()
        }

        self.accounts[username] = account
        self.save_accounts()
        return {"status": "created", "username": username}

    def login(self, username: str, password: str) -> tuple[bool, str]:
        """Вход в систему."""
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
        """Выход из системы."""
        if session_token in self.active_sessions:
            del self.active_sessions[session_token]
            return True
        return False

    def get_profile(self, username: str) -> Optional[dict]:
        """Получить профиль пользователя."""
        if username in self.accounts:
            profile = self.accounts[username].copy()
            profile.pop("password_hash", None)
            return profile
        return None

    def update_profile(self, username: str, updates: dict) -> bool:
        """Обновить профиль."""
        if username not in self.accounts:
            return False

        allowed_fields = ["email", "avatar", "settings"]
        for field, value in updates.items():
            if field in allowed_fields:
                self.accounts[username][field] = value

        self.save_accounts()
        return True

    def change_password(self, username: str, old_password: str,
                       new_password: str) -> tuple[bool, str]:
        """Изменить пароль."""
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
        """Обновить рейтинг."""
        if username in self.accounts:
            self.accounts[username]["rating"] += rating_change
            self.accounts[username]["rating"] = max(0, self.accounts[username]["rating"])
            self.save_accounts()
            return True
        return False

    def record_game_result(self, username: str, result: str) -> bool:
        """Записать результат игры."""
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
        """Получить таблицу лидеров."""
        sorted_accounts = sorted(
            self.accounts.values(),
            key=lambda x: x["rating"],
            reverse=True
        )
        return [
            {
                "username": acc["username"],
                "rating": acc["rating"],
                "games_played": acc["games_played"],
                "wins": acc["wins"]
            }
            for acc in sorted_accounts[:limit]
        ]

    def delete_account(self, username: str, password: str) -> tuple[bool, str]:
        """Удалить аккаунт."""
        if username not in self.accounts:
            return False, "Пользователь не найден"

        password_hash = self._hash_password(password)
        if password_hash != self.accounts[username]["password_hash"]:
            return False, "Неверный пароль"

        del self.accounts[username]
        self.save_accounts()
        return True, "Аккаунт удален"

    def _validate_username(self, username: str) -> bool:
        """Проверка имени пользователя."""
        if len(username) < 3 or len(username) > 20:
            return False
        return username.isalnum()

    def _validate_password(self, password: str) -> bool:
        """Проверка пароля."""
        return len(password) >= 6

    def _hash_password(self, password: str) -> str:
        """Хеширование пароля."""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def _generate_session_token(self, username: str) -> str:
        """Генерация токена сессии."""
        data = f"{username}:{datetime.now().isoformat()}"
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def _default_settings(self) -> dict:
        """Настройки по умолчанию."""
        return {
            "theme": "classic",
            "sound_enabled": True,
            "show_legal_moves": True,
            "auto_queen": False
        }

    def save_accounts(self) -> bool:
        """Сохранить аккаунты в файл."""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.accounts, f, indent=2)
            return True
        except Exception:
            return False

    def load_accounts(self) -> bool:
        """Загрузить аккаунты из файла."""
        try:
            with open(self.storage_path, 'r') as f:
                self.accounts = json.load(f)
            return True
        except FileNotFoundError:
            self.accounts = {}
            return False
        except Exception:
            return False
