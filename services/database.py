import pyodbc
from PyQt6 import QtWidgets
from pathlib import Path

DEFAULT_DB_PATH = r"C:\path\to\default\database.accdb"


def get_db_connection(db_path: str | None = None) -> pyodbc.Connection | None:
    db_path = db_path or DEFAULT_DB_PATH

    if not Path(db_path).exists():
        QtWidgets.QMessageBox.critical(None, "Database Error", f"Database file not found:\n{db_path}")
        return None

    try:
        conn_str = (
            r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
            rf"DBQ={db_path};"
        )
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Database Connection Error", f"Could not connect to database:\n{e}")
        return None
