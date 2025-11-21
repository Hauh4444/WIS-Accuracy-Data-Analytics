"""Resource path resolution for development and PyInstaller bundled environments."""
import os
import sys
from pathlib import Path

APP_NAME = "Accuracy_Report"
DB_FILENAME = "accuracy.db"


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


def get_appdata_db_path() -> Path:
    root = Path(os.getenv("LOCALAPPDATA"))
    app_dir = root / APP_NAME
    app_dir.mkdir(parents=True, exist_ok=True)

    db_path = app_dir / DB_FILENAME

    if not db_path.exists():
        template = Path(resource_path(DB_FILENAME))
        if template.exists():
            db_path.write_bytes(template.read_bytes())
        else:
            db_path.touch()

    return db_path
