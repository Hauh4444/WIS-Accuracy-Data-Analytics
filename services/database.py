import pyodbc
import platform
from PyQt6 import QtWidgets
from pathlib import Path


def get_db_connection(db_path: str) -> pyodbc.Connection | None:
    """Establishes a connection to the Microsoft Access database.
    
    Args:
        db_path: Full path to the database file.

    Returns:
        Active database connection or None if connection fails.
    """
    if not Path(db_path).exists():
        QtWidgets.QMessageBox.critical(None, "Database Error", f"Database file not found:\n{db_path}")
        return None
    if platform.system() != "Windows":
        QtWidgets.QMessageBox.critical(None, "Platform Error", "Windows platform required for Microsoft Access database connectivity.")
        return None

    try:
        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Connection Error", f"Database connection failed:\n{e}")
        return None
