"""Database connection management for Microsoft Access databases via ODBC."""
import pyodbc
import platform
from PyQt6 import QtWidgets
from pathlib import Path

from utils.paths import get_appdata_db_path


def get_storage_db_connection() -> pyodbc.Connection | None:
    """
    Connect to the per-user Access database for storing historical accuracy stats.
    Returns a pyodbc.Connection or None if it fails.
    """
    try:
        db_path = get_appdata_db_path()
        if not db_path.exists() or not db_path.is_file():
            raise FileNotFoundError(f"Storage database not found: {db_path}")

        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
        conn = pyodbc.connect(conn_str, autocommit=False)
        return conn

    except pyodbc.Error as e:
        QtWidgets.QMessageBox.critical(None, "Database Connection Error", f"Failed to connect to storage database:\n{str(e)}")
        return None
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Connection Error", f"Unexpected error connecting to storage database:\n{str(e)}")
        return None



def get_db_connection(db_path: str) -> pyodbc.Connection | None:
    """Establishes a connection to the Microsoft Access database.
    
    Args:
        db_path: Full path to the database file (.mdb or .accdb).

    Returns:
        Active database connection or None if connection fails.
        
    Raises:
        ValueError: If db_path is invalid or platform is not Windows
        RuntimeError: If database connection fails
    """
    try:
        if db_path is None:
            raise ValueError("Database path cannot be None")
        if not isinstance(db_path, str):
            raise ValueError("Database path must be a string")
        if not db_path.strip():
            raise ValueError("Database path cannot be empty")

        db_path_obj = Path(db_path)
        if not db_path_obj.exists():
            raise ValueError(f"Database file not found: {db_path}")
        if not db_path_obj.is_file():
            raise ValueError(f"Database path is not a file: {db_path}")
        if not db_path.lower().endswith(('.mdb', '.accdb')):
            raise ValueError(f"Invalid database file extension. Expected .mdb or .accdb: {db_path}")
        if platform.system() != "Windows":
            raise ValueError("Windows platform required for Microsoft Access database connectivity")

        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
        conn = pyodbc.connect(conn_str, autocommit=False)
        return conn
    except pyodbc.Error as e:
        QtWidgets.QMessageBox.critical(None, "Database Connection Error", f"Failed to connect to database:\n{str(e)}")
        return None
    except ValueError as e:
        QtWidgets.QMessageBox.critical(None, "Configuration Error", f"Database configuration error: {str(e)}")
        return None
    except RuntimeError as e:
        QtWidgets.QMessageBox.critical(None, "Database Error", f"Database operation failed: {str(e)}")
        return None
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Connection Error", f"Unexpected error during database connection:\n{str(e)}")
        return None
