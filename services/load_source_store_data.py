"""Store metadata loader for report headers."""
from datetime import datetime

import pyodbc
from PyQt6 import QtWidgets

from repositories.source_store_repository import fetch_wise_data


def load_source_store_data(conn: pyodbc.Connection) -> dict | None:
    """Load store data for use in report headers.

    Args:
        conn: Database connection object

    Returns:
        Dictionary containing store information for report page headers
        
    Raises:
        ValueError: If connection is invalid or database schema is malformed
        RuntimeError: If critical store data is missing or corrupted
    """
    try:
        if conn is None:
            raise ValueError("Database connection cannot be None")
        if not hasattr(conn, 'cursor'):
            raise ValueError("Invalid database connection object - missing cursor method")

        now = datetime.now()
        store_data: dict = {
            "inventory_datetime": "",
            "print_date": f"{now.month}/{now.day}/{now.year}",
            "store": "",
            "print_time": now.strftime("%I:%M:%S%p"),
            "store_address": ""
        }

        wise_row = fetch_wise_data(conn=conn)
        if wise_row is None or len(wise_row) != 3:
            raise RuntimeError(
                f"Unexpected WISE data structure - expected 3 columns, got {len(wise_row) if wise_row else None}")

        store_data["inventory_datetime"] = wise_row[0] if wise_row[0] is not None else ""
        store_data["store"] = wise_row[1] if wise_row[1] is not None else ""
        store_data["store_address"] = wise_row[2] if wise_row[2] is not None else ""

        return store_data

    except (pyodbc.Error, pyodbc.DatabaseError) as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Database Error",
            f"A database operation failed while loading store metadata.\n\nDetails:\n{str(e)}"
        )
        raise

    except ValueError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Configuration Error",
            f"Invalid database connection or missing required input while preparing store data.\n\nDetails:\n{str(e)}"
        )
        raise

    except RuntimeError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Data Integrity Error",
            f"Critical store metadata was missing or inconsistent during the load process.\n\nDetails:\n{str(e)}"
        )
        raise

    except Exception as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Unexpected Error",
            f"An unexpected failure occurred while loading store metadata.\nThis may indicate corrupt input, missing fields, or an unhandled edge case.\n\nDetails:\n{str(e)}"
        )
        raise