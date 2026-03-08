"""Сохранение и загрузка данных."""

class StorageService:
    def save(self, name: str) -> str:
        return f"{name}.json"
