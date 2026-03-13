"""Сохранение и загрузка данных."""

import json
import os
import pickle
from datetime import datetime
from typing import Any, Optional

class StorageService:
    """Сервис для работы с файловым хранилищем."""

    def __init__(self, base_path: str = "data"):
        self.base_path = base_path
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Создать необходимые директории."""
        directories = [
            self.base_path,
            os.path.join(self.base_path, "games"),
            os.path.join(self.base_path, "replays"),
            os.path.join(self.base_path, "profiles"),
            os.path.join(self.base_path, "backups")
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def save(self, name: str, data: Any, format: str = "json") -> tuple[bool, str]:
        """Сохранить данные в файл."""
        try:
            filepath = self._get_filepath(name, format)
            if format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == "pickle":
                with open(filepath, 'wb') as f:
                    pickle.dump(data, f)
            else:
                return False, "Неподдерживаемый формат"
            return True, filepath
        except Exception as e:
            return False, str(e)

    def load(self, name: str, format: str = "json") -> tuple[bool, Any]:
        """Загрузить данные из файла."""
        try:
            filepath = self._get_filepath(name, format)
            if not os.path.exists(filepath):
                return False, None

            if format == "json":
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            elif format == "pickle":
                with open(filepath, 'rb') as f:
                    data = pickle.load(f)
            else:
                return False, None
            return True, data
        except Exception:
            return False, None

    def save_game(self, game_id: str, game_data: dict) -> bool:
        """Сохранить игру."""
        filepath = os.path.join(self.base_path, "games", f"{game_id}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, indent=2)
            return True
        except Exception:
            return False

    def load_game(self, game_id: str) -> Optional[dict]:
        """Загрузить игру."""
        filepath = os.path.join(self.base_path, "games", f"{game_id}.json")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def save_replay(self, replay_id: str, replay_data: dict) -> bool:
        """Сохранить повтор."""
        filepath = os.path.join(self.base_path, "replays", f"{replay_id}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(replay_data, f, indent=2)
            return True
        except Exception:
            return False

    def load_replay(self, replay_id: str) -> Optional[dict]:
        """Загрузить повтор."""
        filepath = os.path.join(self.base_path, "replays", f"{replay_id}.json")
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def list_games(self) -> list[str]:
        """Получить список сохраненных игр."""
        games_dir = os.path.join(self.base_path, "games")
        try:
            files = os.listdir(games_dir)
            return [f.replace('.json', '') for f in files if f.endswith('.json')]
        except Exception:
            return []

    def list_replays(self) -> list[str]:
        """Получить список повторов."""
        replays_dir = os.path.join(self.base_path, "replays")
        try:
            files = os.listdir(replays_dir)
            return [f.replace('.json', '') for f in files if f.endswith('.json')]
        except Exception:
            return []

    def delete_game(self, game_id: str) -> bool:
        """Удалить игру."""
        filepath = os.path.join(self.base_path, "games", f"{game_id}.json")
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception:
            return False

    def delete_replay(self, replay_id: str) -> bool:
        """Удалить повтор."""
        filepath = os.path.join(self.base_path, "replays", f"{replay_id}.json")
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception:
            return False

    def create_backup(self, name: str = None) -> tuple[bool, str]:
        """Создать резервную копию."""
        if name is None:
            name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        backup_path = os.path.join(self.base_path, "backups", name)
        try:
            os.makedirs(backup_path, exist_ok=True)

            # Копируем все данные
            import shutil
            for subdir in ["games", "replays", "profiles"]:
                src = os.path.join(self.base_path, subdir)
                dst = os.path.join(backup_path, subdir)
                if os.path.exists(src):
                    shutil.copytree(src, dst, dirs_exist_ok=True)

            return True, backup_path
        except Exception as e:
            return False, str(e)

    def restore_backup(self, backup_name: str) -> bool:
        """Восстановить из резервной копии."""
        backup_path = os.path.join(self.base_path, "backups", backup_name)
        if not os.path.exists(backup_path):
            return False

        try:
            import shutil
            for subdir in ["games", "replays", "profiles"]:
                src = os.path.join(backup_path, subdir)
                dst = os.path.join(self.base_path, subdir)
                if os.path.exists(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
            return True
        except Exception:
            return False

    def get_storage_info(self) -> dict:
        """Получить информацию о хранилище."""
        info = {
            "games_count": len(self.list_games()),
            "replays_count": len(self.list_replays()),
            "total_size": self._get_directory_size(self.base_path),
            "backups_count": len(self.list_backups())
        }
        return info

    def list_backups(self) -> list[str]:
        """Получить список резервных копий."""
        backups_dir = os.path.join(self.base_path, "backups")
        try:
            return [d for d in os.listdir(backups_dir)
                   if os.path.isdir(os.path.join(backups_dir, d))]
        except Exception:
            return []

    def _get_filepath(self, name: str, format: str) -> str:
        """Получить полный путь к файлу."""
        extension = "json" if format == "json" else "pkl"
        return os.path.join(self.base_path, f"{name}.{extension}")

    def _get_directory_size(self, path: str) -> int:
        """Получить размер директории в байтах."""
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception:
            pass
        return total_size

    def export_data(self, output_path: str) -> bool:
        """Экспортировать все данные."""
        try:
            import shutil
            shutil.make_archive(output_path, 'zip', self.base_path)
            return True
        except Exception:
            return False

    def import_data(self, archive_path: str) -> bool:
        """Импортировать данные из архива."""
        try:
            import shutil
            shutil.unpack_archive(archive_path, self.base_path)
            return True
        except Exception:
            return False
