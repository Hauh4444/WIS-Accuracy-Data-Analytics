"""Resource path resolution for development and PyInstaller bundled environments."""
import os
import sys
from pathlib import Path

APP_NAME = "Accuracy_Report"
DB_FILENAME = "accuracy.mdb"
LOG_FILENAME = "app.log"


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller.
    
    - PyInstaller extracts bundled files to a temp folder and sets sys._MEIPASS.
    
    Args:
        relative_path: Path relative to the project root
        
    Returns:
        Absolute path to the resource file
    """
    try:
        # noinspection PyProtectedMember,PyUnresolvedReferences
        base_path = sys._MEIPASS

    except (AttributeError, Exception):
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)


def get_appdata_root() -> Path:
    root = Path(os.getenv("LOCALAPPDATA")) / APP_NAME
    root.mkdir(parents=True, exist_ok=True)
    return root


def get_appdata_db_path() -> Path:
    """Get the path to the local application database in the user's AppData folder.

    Returns:
       Path: Absolute Path object pointing to the local database file.
    """
    root = get_appdata_root()
    db_path = root / DB_FILENAME
    if not db_path.exists():
        template = Path(resource_path(f"assets/resources/{DB_FILENAME}"))
        db_path.write_bytes(template.read_bytes())

    return db_path

def get_log_path() -> Path:
    log_dir = get_appdata_root() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / LOG_FILENAME