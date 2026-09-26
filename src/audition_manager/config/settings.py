import os
import sys
from pathlib import Path


def application_data_directory() -> Path:
    override = os.environ.get("AUDITION_MANAGER_DATA_DIR")
    if override:
        return Path(override).expanduser()
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "Audition Manager"
    base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "audition-manager"


def database_path() -> Path:
    return application_data_directory() / "library.sqlite3"
