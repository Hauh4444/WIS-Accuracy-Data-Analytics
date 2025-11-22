"""Store metadata loader for report headers."""
import pyodbc
from datetime import datetime
from PyQt6 import QtWidgets

from repositories.local_store_repository import fetch_inventory_data, fetch_season_inventory_data


def load_local_store_data(conn: pyodbc.Connection, store: str | None) -> dict | None:
    """Load store data for use in report headers.

    Args:
        conn: Database connection object
        store: Store number inputted by user or None if retrieving season stats

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

        if not store:
            inventory_rows = fetch_season_inventory_data(conn=conn)
            if inventory_rows:
                dates = [datetime.strptime(row[0], "%m/%d/%Y %I:%M:%S %p") for row in inventory_rows]
                store_data["season_range"] = f"{max(dates).strftime('%b %Y')} - {min(dates).strftime('%b %Y')}"
            else:
                store_data["season_range"] = None
        else:
            inventory_row = fetch_inventory_data(conn=conn, store=store)
            if inventory_row is None or len(inventory_row) != 3:
                raise RuntimeError(
                    f"Unexpected Inventory data structure - expected 3 columns, got {len(inventory_row) if inventory_row else None}")

            store_data["inventory_datetime"] = inventory_row[0] if inventory_row[0] is not None else ""
            store_data["store"] = inventory_row[1] if inventory_row[1] is not None else ""
            store_data["store_address"] = inventory_row[2] if inventory_row[2] is not None else ""

        return store_data

    except (pyodbc.Error, pyodbc.DatabaseError) as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Database Error",
            f"A database operation failed while loading local or season store data.\n\nDetails:\n{str(e)}"
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
            f"Critical inventory or store data was missing or inconsistent during the load process.\n\nDetails:\n{str(e)}"
        )
        raise

    except Exception as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Unexpected Error",
            f"An unexpected failure occurred while loading store data.\nThis may indicate corrupt input, missing fields, or an unhandled edge case.\n\nDetails:\n{str(e)}"
        )
        raise