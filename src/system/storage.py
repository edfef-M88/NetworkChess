"""Файловое хранилище: сохранение, загрузка, бэкапы, импорт/экспорт.

Модуль реализует сервис :class:`StorageService`, который отвечает за работу с
данными приложения на диске. В учебном проекте NetworkChess он используется для
сериализации:

- сохранённых партий (games/*.json);
- повторов (replays/*.json);
- профилей (profiles/* — в данной версии директория зарезервирована);
- резервных копий (backups/*).

Сервис поддерживает два базовых формата сериализации:

- JSON (читаемый, подходит для большинства структур);
- pickle (бинарный, потенциально небезопасен для недоверенных данных).

Внимание по безопасности: загрузка pickle-файлов из недоверенного источника может
приводить к выполнению произвольного кода. В рамках лабораторной работы это
приемлемо как демонстрация формата, но в реальном приложении следует избегать
pickle для пользовательских/внешних данных.

Classes:
    StorageService: Работа с файлами данных, бэкапами и импортом/экспортом.
"""

import json
import os
import pickle
from datetime import datetime
from typing import Any, Optional


class StorageService:
    """Сервис для работы с файловым хранилищем проекта.

    Экземпляр сервиса управляет базовой директорией данных и предоставляет
    операции сохранения/загрузки, перечисления объектов, удаления и создания
    резервных копий.

    Attributes:
        base_path: Корневая директория хранения данных (по умолчанию "data").
    """

    def __init__(self, base_path: str = "data") -> None:
        """Создать сервис хранения и подготовить структуру директорий.

        Args:
            base_path: Путь к корневой директории хранилища.

        Returns:
            None
        """
        self.base_path = base_path
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Создать необходимые поддиректории хранилища.

        Returns:
            None
        """
        directories = [
            self.base_path,
            os.path.join(self.base_path, "games"),
            os.path.join(self.base_path, "replays"),
            os.path.join(self.base_path, "profiles"),
            os.path.join(self.base_path, "backups"),
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)

    def save(self, name: str, data: Any, format: str = "json") -> tuple[bool, str]:
        """Сохранить произвольные данные в файл в формате JSON или pickle.

        Args:
            name: Базовое имя файла (без расширения).
            data: Сериализуемые данные.
            format: Формат сохранения: "json" или "pickle".

        Returns:
            tuple[bool, str]:

            - (True, filepath) при успешном сохранении;
            - (False, reason) при ошибке.

        Raises:
            None: Исключения перехватываются и преобразуются в (False, str).
        """
        try:
            filepath = self._get_filepath(name, format)
            if format == "json":
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format == "pickle":
                with open(filepath, "wb") as f:
                    pickle.dump(data, f)
            else:
                return False, "Неподдерживаемый формат"
            return True, filepath
        except Exception as e:
            return False, str(e)

    def load(self, name: str, format: str = "json") -> tuple[bool, Any]:
        """Загрузить данные из файла в формате JSON или pickle.

        Args:
            name: Базовое имя файла (без расширения).
            format: Формат чтения: "json" или "pickle".

        Returns:
            tuple[bool, Any]:

            - (True, data) при успешной загрузке;
            - (False, None) если файл не найден или произошла ошибка.
        """
        try:
            filepath = self._get_filepath(name, format)
            if not os.path.exists(filepath):
                return False, None

            if format == "json":
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
            elif format == "pickle":
                with open(filepath, "rb") as f:
                    data = pickle.load(f)
            else:
                return False, None
            return True, data
        except Exception:
            return False, None

    def save_game(self, game_id: str, game_data: dict) -> bool:
        """Сохранить данные партии в каталог games/.

        Args:
            game_id: Идентификатор партии (используется как имя файла).
            game_data: Сериализуемые данные партии.

        Returns:
            bool: True, если запись прошла успешно.
        """
        filepath = os.path.join(self.base_path, "games", f"{game_id}.json")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(game_data, f, indent=2)
            return True
        except Exception:
            return False

    def load_game(self, game_id: str) -> Optional[dict]:
        """Загрузить сохранённую партию из каталога games/.

        Args:
            game_id: Идентификатор партии (имя файла без расширения).

        Returns:
            Optional[dict]: Данные партии либо None, если чтение не удалось.
        """
        filepath = os.path.join(self.base_path, "games", f"{game_id}.json")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def save_replay(self, replay_id: str, replay_data: dict) -> bool:
        """Сохранить данные повтора в каталог replays/.

        Args:
            replay_id: Идентификатор повтора.
            replay_data: Сериализуемые данные повтора.

        Returns:
            bool: True, если запись прошла успешно.
        """
        filepath = os.path.join(self.base_path, "replays", f"{replay_id}.json")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(replay_data, f, indent=2)
            return True
        except Exception:
            return False

    def load_replay(self, replay_id: str) -> Optional[dict]:
        """Загрузить сохранённый повтор из каталога replays/.

        Args:
            replay_id: Идентификатор повтора.

        Returns:
            Optional[dict]: Данные повтора либо None, если чтение не удалось.
        """
        filepath = os.path.join(self.base_path, "replays", f"{replay_id}.json")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def list_games(self) -> list[str]:
        """Получить список идентификаторов сохранённых партий.

        Returns:
            list[str]: Имена файлов без расширения .json.
        """
        games_dir = os.path.join(self.base_path, "games")
        try:
            files = os.listdir(games_dir)
            return [f.replace(".json", "") for f in files if f.endswith(".json")]
        except Exception:
            return []

    def list_replays(self) -> list[str]:
        """Получить список идентификаторов сохранённых повторов.

        Returns:
            list[str]: Имена файлов без расширения .json.
        """
        replays_dir = os.path.join(self.base_path, "replays")
        try:
            files = os.listdir(replays_dir)
            return [f.replace(".json", "") for f in files if f.endswith(".json")]
        except Exception:
            return []

    def delete_game(self, game_id: str) -> bool:
        """Удалить сохранённую партию.

        Args:
            game_id: Идентификатор партии.

        Returns:
            bool: True, если файл был удалён.
        """
        filepath = os.path.join(self.base_path, "games", f"{game_id}.json")
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception:
            return False

    def delete_replay(self, replay_id: str) -> bool:
        """Удалить сохранённый повтор.

        Args:
            replay_id: Идентификатор повтора.

        Returns:
            bool: True, если файл был удалён.
        """
        filepath = os.path.join(self.base_path, "replays", f"{replay_id}.json")
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception:
            return False

    def create_backup(self, name: str | None = None) -> tuple[bool, str]:
        """Создать резервную копию данных games/replays/profiles.

        Args:
            name: Имя папки бэкапа. Если None, генерируется имя на основе времени.

        Returns:
            tuple[bool, str]:

            - (True, backup_path) если бэкап создан;
            - (False, reason) если произошла ошибка.
        """
        if name is None:
            name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        backup_path = os.path.join(self.base_path, "backups", name)
        try:
            os.makedirs(backup_path, exist_ok=True)

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
        """Восстановить данные из резервной копии.

        Метод перезаписывает текущие поддиректории games/replays/profiles.

        Args:
            backup_name: Имя папки бэкапа в backups/.

        Returns:
            bool: True, если восстановление прошло успешно.
        """
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
        """Получить агрегированную информацию о текущем состоянии хранилища.

        Returns:
            dict: Словарь с полями games_count, replays_count, total_size,
            backups_count.
        """
        return {
            "games_count": len(self.list_games()),
            "replays_count": len(self.list_replays()),
            "total_size": self._get_directory_size(self.base_path),
            "backups_count": len(self.list_backups()),
        }

    def list_backups(self) -> list[str]:
        """Получить список доступных резервных копий.

        Returns:
            list[str]: Имена директорий в backups/.
        """
        backups_dir = os.path.join(self.base_path, "backups")
        try:
            return [d for d in os.listdir(backups_dir) if os.path.isdir(os.path.join(backups_dir, d))]
        except Exception:
            return []

    def _get_filepath(self, name: str, format: str) -> str:
        """Построить путь к файлу в base_path по имени и формату.

        Args:
            name: Базовое имя файла (без расширения).
            format: "json" или "pickle".

        Returns:
            str: Полный путь к файлу.
        """
        extension = "json" if format == "json" else "pkl"
        return os.path.join(self.base_path, f"{name}.{extension}")

    def _get_directory_size(self, path: str) -> int:
        """Подсчитать суммарный размер директории.

        Args:
            path: Путь к директории.

        Returns:
            int: Размер в байтах.
        """
        total_size = 0
        try:
            for dirpath, _dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
        except Exception:
            pass
        return total_size

    def export_data(self, output_path: str) -> bool:
        """Экспортировать данные хранилища в ZIP-архив.

        Args:
            output_path: Путь/префикс для архива (используется shutil.make_archive).

        Returns:
            bool: True, если архив был создан.
        """
        try:
            import shutil

            shutil.make_archive(output_path, "zip", self.base_path)
            return True
        except Exception:
            return False

    def import_data(self, archive_path: str) -> bool:
        """Импортировать данные из архива в base_path.

        Args:
            archive_path: Путь к ZIP (или другому поддерживаемому) архиву.

        Returns:
            bool: True, если распаковка прошла успешно.
        """
        try:
            import shutil

            shutil.unpack_archive(archive_path, self.base_path)
            return True
        except Exception:
            return False
