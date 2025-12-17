"""Database connection management for Microsoft Access databases via ODBC."""
import pyodbc
import platform
import logging
from PyQt6 import QtWidgets
from pathlib import Path

from utils import get_appdata_db_path


def get_db_connection(db_path: str) -> pyodbc.Connection | None:
    """Establishes a connection to the Microsoft Access database.

    Args:
        db_path: Full path to the database file (.mdb or .accdb).

    Returns:
        Active database connection or None if connection fails.
    """
    try:
        if db_path is None or not isinstance(db_path, str) or not db_path.strip():
            raise ValueError("Database path must be a non-empty string")
        db_path_obj = Path(db_path)
        if not db_path_obj.exists() or not db_path_obj.is_file():
            raise ValueError(f"Source database file not found: {db_path}")
        if not db_path.lower().endswith(('.mdb', '.accdb')):
            raise ValueError(f"Invalid database file extension: {db_path}")
        if platform.system() != "Windows":
            raise ValueError("Windows platform required for Access DB connectivity")

        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
        return pyodbc.connect(conn_str, autocommit=False)

    except Exception as e:
        logging.exception(f"Failed to connect to Access database at {db_path}")
        QtWidgets.QMessageBox.warning(
            None,
            "Database Connection Error",
            f"Could not connect to Access database at {db_path}.\n\nDetails:\n{str(e)}"
        )
        return None


def get_storage_db_connection() -> pyodbc.Connection | None:
    """Connect to the per-user Access database for storing historical accuracy stats.

    Returns:
        Active database connection or None if connection fails.
    """
    db_path = None
    try:
        db_path = get_appdata_db_path()
        if not db_path.exists() or not db_path.is_file():
            raise FileNotFoundError(f"Storage database file not found: {db_path}")
        if platform.system() != "Windows":
            raise ValueError("Windows platform required for Access DB connectivity")

        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
        return pyodbc.connect(conn_str, autocommit=False)

    except Exception as e:
        logging.exception(f"Failed to connect to storage database at {db_path}")
        QtWidgets.QMessageBox.warning(
            None,
            "Storage Database Connection Error",
            f"Could not connect to storage database at {db_path}.\n\nDetails:\n{str(e)}"
        )
        return None