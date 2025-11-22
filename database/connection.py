"""Database connection management for Microsoft Access databases via ODBC."""
import pyodbc
import platform
import traceback
from PyQt6 import QtWidgets
from pathlib import Path

from utils.paths import get_appdata_db_path


def get_db_connection(db_path: str) -> pyodbc.Connection | None:
    """Establishes a connection to the Microsoft Access database.

    Args:
        db_path: Full path to the database file (.mdb or .accdb).

    Returns:
        Active database connection or None if connection fails.
    """
    try:
        if db_path is None:
            raise ValueError("Database path cannot be None")
        if not isinstance(db_path, str):
            raise ValueError("Database path must be a string")
        if not db_path.strip():
            raise ValueError("Database path cannot be empty")

        db_path_obj = Path(db_path)
        if not db_path_obj.exists() or not db_path_obj.is_file():
            raise ValueError(f"Source database file not found: {db_path}")
        if not db_path.lower().endswith(('.mdb', '.accdb')):
            raise ValueError(f"Invalid database file extension. Expected .mdb or .accdb: {db_path}")
        if platform.system() != "Windows":
            raise ValueError("Windows platform required for Microsoft Access database connectivity")

        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
        conn = pyodbc.connect(conn_str, autocommit=False)
        return conn

    except pyodbc.Error as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Database Connection Error",
            f"A database operation failed while attempting to connect to the Access database.\n\nDetails:\n{str(e)}"
        )
        traceback.print_exc()
        return None

    except ValueError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Configuration Error",
            f"Invalid database configuration or path provided.\nPlease verify the database file exists and the path is correct.\n\nDetails:\n{str(e)}"
        )
        traceback.print_exc()
        return None

    except RuntimeError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Database Error",
            f"A critical database operation failed while establishing the connection.\n\nDetails:\n{str(e)}"
        )
        traceback.print_exc()
        return None

    except Exception as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Unexpected Error",
            f"An unexpected error occurred while connecting to the database.\nThis may indicate corrupt files, missing drivers, or an unhandled edge case.\n\nDetails:\n{str(e)}"
        )
        traceback.print_exc()
        return None


def get_storage_db_connection() -> pyodbc.Connection | None:
    """Connect to the per-user Access database for storing historical accuracy stats.

    Returns:
        Active database connection or None if connection fails.
    """
    try:
        db_path = get_appdata_db_path()
        if not db_path.exists() or not db_path.is_file():
            raise FileNotFoundError(f"Storage database file not found: {db_path}")
        if platform.system() != "Windows":
            raise ValueError("Windows platform required for Microsoft Access database connectivity")

        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
        conn = pyodbc.connect(conn_str, autocommit=False)
        return conn

    except pyodbc.Error as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Database Connection Error",
            f"A database operation failed while attempting to connect to the storage database.\n\nDetails:\n{str(e)}"
        )
        traceback.print_exc()
        return None

    except ValueError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Configuration Error",
            f"Invalid configuration or unsupported platform while connecting to the storage database.\n\nDetails:\n{str(e)}"
        )
        traceback.print_exc()
        return None

    except RuntimeError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Database Error",
            f"A critical database operation failed while connecting to the storage database.\n\nDetails:\n{str(e)}"
        )
        traceback.print_exc()
        return None

    except Exception as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Unexpected Error",
            f"An unexpected failure occurred while connecting to the storage database.\nThis may indicate corrupt files, missing drivers, or an unhandled edge case.\n\nDetails:\n{str(e)}"
        )
        traceback.print_exc()
        return None