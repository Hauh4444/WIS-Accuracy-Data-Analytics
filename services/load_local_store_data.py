"""Store metadata loader for report headers."""
import pyodbc
import logging
from datetime import datetime
from PyQt6 import QtWidgets

from repositories import fetch_old_inventory_data


def load_local_store_data(conn: pyodbc.Connection, store: str | None, date_range: list[datetime] | None) -> dict | None:
    """Load store data for use in report headers.

    Args:
        conn: Database connection object
        store: Store number inputted by user or None if retrieving season stats
        date_range: Range of datetimes inputted by user or None if retrieving store stats

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
            "print_date": f"{now.month}/{now.day}/{now.year}",
            "print_time": now.strftime("%I:%M:%S%p"),
        }

        if store:
            inventory_row = fetch_old_inventory_data(conn, store)
            if inventory_row is None or len(inventory_row) != 3:
                raise RuntimeError(
                    f"Unexpected Inventory data structure - expected 3 columns, got {len(inventory_row) if inventory_row else None}")

            store_data["inventory_datetime"] = inventory_row[0] or ""
            store_data["store"] = inventory_row[1] or ""
            store_data["store_address"] = inventory_row[2] or ""
        else:
            store_data["start_date"] = date_range[0].strftime("%m/%d/%Y")
            store_data["end_date"] = date_range[1].strftime("%m/%d/%Y")

        return store_data

    except (pyodbc.Error, pyodbc.DatabaseError) as e:
        logging.exception("Database error while loading local store data")
        QtWidgets.QMessageBox.warning(
            None,
            "Database Error",
            f"A database operation failed while loading local or season store data.\n\nDetails:\n{str(e)}"
        )
        raise

    except ValueError as e:
        logging.exception("Configuration error while loading local store data")
        QtWidgets.QMessageBox.warning(
            None,
            "Configuration Error",
            f"Invalid database connection or missing required input while preparing store data.\n\nDetails:\n{str(e)}"
        )
        raise

    except RuntimeError as e:
        logging.exception("Data integrity error while loading local store data")
        QtWidgets.QMessageBox.warning(
            None,
            "Data Integrity Error",
            f"Critical inventory or store data was missing or inconsistent during the load process.\n\nDetails:\n{str(e)}"
        )
        raise

    except Exception as e:
        logging.exception("Unhandled error while loading local store data")
        QtWidgets.QMessageBox.warning(
            None,
            "Unexpected Error",
            f"An unexpected failure occurred while loading store data.\n\nDetails:\n{str(e)}"
        )
        raise