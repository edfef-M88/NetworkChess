"""Учётные записи и профили пользователей."""

class AccountService:
    def register(self, username: str) -> dict:
        return {"username": username, "status": "created"}
