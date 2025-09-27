import pyodbc
import platform
from PyQt6 import QtWidgets
from pathlib import Path

def get_db_connection(db_path: str | None = None, job_id: str | None = None) -> pyodbc.Connection | None:
    """Establish database connection with platform-specific driver selection.
    
    Args:
        db_path: Path to the database file. If None, will use default path with job_id.
        job_id: Job ID to use for default database path construction.
        
    Returns:
        Database connection object or None if connection fails.
    """
    if db_path is None and job_id is not None:
        db_path = rf"C:\WISDOM\JOBS\{job_id}\11355\{job_id}.MDB"
    elif db_path is None and job_id is None:
        try:
            QtWidgets.QMessageBox.critical(None, "Database Error", "Either db_path or job_id must be provided to establish database connection.")
        except:
            print("Database Error: Either db_path or job_id must be provided to establish database connection.")
        return None

    if not Path(db_path).exists():
        try:
            QtWidgets.QMessageBox.critical(None, "Database Error", f"Database file not found:\n{db_path}")
        except:
            print(f"Database Error: Database file not found:\n{db_path}")
        return None

    try:
        if platform.system() == "Windows":
            conn_str = (
                r"DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};"
                rf"DBQ={db_path};"
            )
        else:
            conn_str = (
                r"DRIVER={MDBTools};"
                rf"DBQ={db_path};"
            )
        
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        error_msg = f"Could not connect to database:\n{e}"
        
        if platform.system() != "Windows":
            error_msg += "\n\nNote: On Linux, you may need to install MDBTools:"
            error_msg += "\nsudo apt-get install mdbtools"
            error_msg += "\n\nOr use a Windows machine for production deployment."
        
        try:
            QtWidgets.QMessageBox.critical(None, "Database Connection Error", error_msg)
        except:
            print(f"Database Connection Error: {error_msg}")
        return None
