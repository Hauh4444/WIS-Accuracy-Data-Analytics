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
                f"Unexpected WISE data structure - expected 3 columns, got {len(wise_row) if wise_row else 0}")

        inventory_datetime, store_name, store_address = wise_row
        if not store_name or not str(store_name).strip():
            raise RuntimeError("Store name is missing or empty - required for report headers")
        if inventory_datetime and hasattr(inventory_datetime, 'year'):
            if inventory_datetime.year > now.year + 1:
                raise RuntimeError(f"Invalid inventory datetime: {inventory_datetime} appears to be in the future")

        store_data["inventory_datetime"] = inventory_datetime if inventory_datetime is not None else ""
        store_data["store"] = str(store_name).strip() if store_name is not None else ""
        store_data["store_address"] = str(store_address).strip() if store_address is not None else ""
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