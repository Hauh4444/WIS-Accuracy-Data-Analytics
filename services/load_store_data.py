"""Store metadata loader for report headers."""
import pyodbc
from PyQt6 import QtWidgets
from datetime import datetime

from repositories.store_repository import fetch_wise_data


def load_store_data(conn: pyodbc.Connection) -> dict:
    """Load store data for use in report headers.

    Args:
        conn: Database connection object

    Returns:
        Dictionary containing store information for report page headers
        
    Raises:
        ValueError: If connection is invalid or database schema is malformed
        RuntimeError: If critical store data is missing or corrupted
    """
    now = datetime.now()
    store_data = {
        "inventory_datetime": "",
        "print_date": f"{now.month}/{now.day}/{now.year}",
        "store": "",
        "print_time": now.strftime("%I:%M:%S%p"),
        "store_address": ""
    }

    try:
        if conn is None:
            raise ValueError("Database connection cannot be None")
        if not hasattr(conn, 'cursor'):
            raise ValueError("Invalid database connection object - missing cursor method")

        wise_row = fetch_wise_data(conn=conn)
        if wise_row is None or len(wise_row) != 3:
            raise RuntimeError(
                f"Unexpected WISE data structure - expected 3 columns, got {len(wise_row) if wise_row else None}")

        store_data["inventory_datetime"] = wise_row[0] if wise_row[0] is not None else ""
        store_data["store_name"] = wise_row[1] if wise_row[1] is not None else ""
        store_data["store_address"] = wise_row[2] if wise_row[2] is not None else ""
    except (pyodbc.Error, pyodbc.DatabaseError) as e:
        QtWidgets.QMessageBox.critical(None, "Database Error", f"Database query failed: {str(e)}")
        raise 
    except ValueError as e:
        QtWidgets.QMessageBox.critical(None, "Configuration Error", f"Invalid configuration: {str(e)}")
        raise
    except RuntimeError as e:
        QtWidgets.QMessageBox.critical(None, "Data Error", f"Data validation failed: {str(e)}")
        raise
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Unexpected Error", f"An unexpected error occurred: {str(e)}")
        raise

    return store_data