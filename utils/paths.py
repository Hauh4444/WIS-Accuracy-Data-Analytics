"""Resource path resolution for development and PyInstaller bundled environments."""
import os
import sys
import json
from pathlib import Path

APP_NAME = "Accuracy_Report"


def read_config_file() -> dict | None:
    """Get the contents of the config file in the AppData folder.

    Returns:
       Dictionary containing config data.
    """
    config_path = os.path.join(get_appdata_root(), "config.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as file:
        return json.load(file)


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller.

    Args:
        relative_path: Path relative to the project root

    Returns:
        Absolute path object pointing to the resource file
    """
    try:
        base_path = sys._MEIPASS

    except (AttributeError, Exception):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)


def get_appdata_root() -> Path:
    """Get the path to the user's AppData folder.

    Returns:
       Absolute Path object pointing to the AppData folder.
    """
    root = Path(os.getenv("LOCALAPPDATA")) / APP_NAME
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_db_path() -> Path:
    """Get the path to the local application database in the user's AppData folder.

    Returns:
       Absolute Path object pointing to the local database file.
    """
    config = read_config_file()
    root = Path(os.path.expandvars(config["local_data_path"]))
    db_filename = config["database_filename"]
    db_path = root / db_filename
    print(db_path)
    if not db_path.exists():
        template = Path(resource_path(f"assets/resources/{db_filename}"))
        db_path.write_bytes(template.read_bytes())

    return db_path


def get_log_path() -> Path:
    """Return the path to the log file, creating the logs folder if needed.

    Returns:
        Absolute Path object pointing to the log file.
    """
    log_dir = get_appdata_root() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    config = read_config_file()
    log_filename = config["database_filename"]
    return log_dir / log_filename