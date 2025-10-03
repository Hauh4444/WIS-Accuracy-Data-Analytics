import pyodbc
import platform
from PyQt6 import QtWidgets
from pathlib import Path


def get_db_connection(db_path: str | None = None, job_number: str | None = None) -> pyodbc.Connection | None:
    """Establishes a connection to the Microsoft Access database.
    
    Args:
        db_path: Full path to the database file. If not provided, constructs path using job_number.
        job_number: Job number for default database path construction.
        
    Returns:
        Active database connection or None if connection fails.
    """
    if db_path is None and job_number is not None:
        db_path = rf"C:\WISDOM\JOBS\{job_number}\11355\{job_number}.MDB"
    elif db_path is None and job_number is None:
        try:
            QtWidgets.QMessageBox.critical(None, "Database Error", "Database path or job number required for connection.")
        except:
            print("Database Error: Database path or job number required for connection.")
        return None

    if not Path(db_path).exists():
        try:
            QtWidgets.QMessageBox.critical(None, "Database Error", f"Database file not found:\n{db_path}")
        except:
            print(f"Database Error: Database file not found: {db_path}")
        return None

    try:
        if platform.system() != "Windows":
            error_msg = "Windows platform required for Microsoft Access database connectivity."
            try:
                QtWidgets.QMessageBox.critical(None, "Platform Error", error_msg)
            except:
                print(f"Platform Error: {error_msg}")
            return None
            
        conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={db_path};"
        
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        error_msg = f"Database connection failed:\n{e}"
        try:
            QtWidgets.QMessageBox.critical(None, "Connection Error", error_msg)
        except:
            print(f"Connection Error: {error_msg}")
        return None
