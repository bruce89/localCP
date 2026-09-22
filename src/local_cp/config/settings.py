from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QSettings


class AppSettings:
    """Persist non-secret desktop preferences with Qt's platform storage."""

    def __init__(self) -> None:
        self._settings = QSettings()

    def last_project(self) -> Path | None:
        value = self._settings.value("projects/last_directory", "", str)
        if not value:
            return None
        path = Path(value)
        return path if path.is_dir() else None

    def set_last_project(self, path: Path) -> None:
        self._settings.setValue("projects/last_directory", str(path))
