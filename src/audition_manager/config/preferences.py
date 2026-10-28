import json
import os
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class UserPreferences:
    last_di_file: Path | None = None
    last_ir_directory: Path | None = None
    last_capture_directory: Path | None = None
    last_capture_file: Path | None = None
    last_export_directory: Path | None = None
    output_device_name: str | None = None
    output_host_api: str | None = None
    output_gain_db: int = 0
    capture_gain_db: int = 0
    loop_enabled: bool = True


class PreferencesStore:
    VERSION = 1

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> UserPreferences:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return UserPreferences()
        if not isinstance(payload, dict) or payload.get("version") != self.VERSION:
            return UserPreferences()
        gain = payload.get("output_gain_db", 0)
        if not isinstance(gain, int) or isinstance(gain, bool):
            gain = 0
        capture_gain = payload.get("capture_gain_db", 0)
        if not isinstance(capture_gain, int) or isinstance(capture_gain, bool):
            capture_gain = 0
        return UserPreferences(
            last_di_file=self._path(payload.get("last_di_file")),
            last_ir_directory=self._path(payload.get("last_ir_directory")),
            last_capture_directory=self._path(payload.get("last_capture_directory")),
            last_capture_file=self._path(payload.get("last_capture_file")),
            last_export_directory=self._path(payload.get("last_export_directory")),
            output_device_name=self._text(payload.get("output_device_name")),
            output_host_api=self._text(payload.get("output_host_api")),
            output_gain_db=max(-24, min(0, gain)),
            capture_gain_db=max(-24, min(12, capture_gain)),
            loop_enabled=(
                payload["loop_enabled"]
                if isinstance(payload.get("loop_enabled"), bool)
                else True
            ),
        )

    def save(self, preferences: UserPreferences) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = asdict(preferences)
        payload["version"] = self.VERSION
        for key in (
            "last_di_file", "last_ir_directory", "last_capture_directory",
            "last_capture_file", "last_export_directory",
        ):
            value = payload[key]
            payload[key] = str(value) if value is not None else None
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{self.path.name}.", suffix=".tmp", dir=self.path.parent
        )
        temporary_path = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as temporary:
                json.dump(payload, temporary, ensure_ascii=False, indent=2)
                temporary.write("\n")
                temporary.flush()
                os.fsync(temporary.fileno())
            os.replace(temporary_path, self.path)
        finally:
            temporary_path.unlink(missing_ok=True)

    @staticmethod
    def _path(value: object) -> Path | None:
        return Path(value).expanduser() if isinstance(value, str) and value else None

    @staticmethod
    def _text(value: object) -> str | None:
        return value if isinstance(value, str) and value else None
