"""zone data loader with inventory accuracy metrics."""
import pyodbc
import logging
from PyQt6 import QtWidgets
from datetime import datetime

from repositories import fetch_historical_zone_data, fetch_aggregate_zone_data


def load_local_zone_data(conn: pyodbc.Connection, store: str | None, date_range: list[datetime] | None = None) -> list[dict] | None:
    """Load zone data with discrepancy calculations.

    Args:
        conn: Database connection object
        store: Store number inputted by user or None if retrieving aggregate stats
        date_range: Range of datetimes inputted by user or None if retrieving store stats

    Returns:
        List of dictionaries containing zone data with totals and discrepancies

    Raises:
        ValueError: If connection is invalid or database schema is malformed
        RuntimeError: If critical zone data is missing or corrupted
    """
    try:
        if conn is None:
            raise ValueError("Database connection cannot be None")
        if not hasattr(conn, 'cursor'):
            raise ValueError("Invalid database connection object - missing cursor method")
        if not (store or date_range):
            raise ValueError("Either store or range must be set")
        if date_range and len(date_range) != 2:
            raise ValueError("date_range must contain exactly two datetime objects")

        if store:
            zone_rows = fetch_historical_zone_data(conn, store)
        else:
            zone_rows = fetch_aggregate_zone_data(conn, date_range)

        zone_data: list[dict] = []

        for zone_row in zone_rows:
            zone_data_row = {
                "zone_id": zone_row[0] or "",
                "zone_description": zone_row[1] or "",
                "total_tags": zone_row[2] or 0,
                "total_quantity": zone_row[3] or 0,
                "total_price": zone_row[4] or 0.0,
                "discrepancy_dollars": zone_row[5] or 0.0,
                "discrepancy_tags": zone_row[6] or 0,
                "stores": (zone_row[7] or 1) if date_range else None
            }
            zone_data_row["discrepancy_percent"] = (zone_data_row["discrepancy_dollars"] / zone_data_row["total_price"] * 100) if zone_data_row["total_price"] > 0 else 0
            zone_data.append(zone_data_row)

        return zone_data

    except (pyodbc.Error, pyodbc.DatabaseError) as e:
        logging.exception("Database error while loading local zone data")
        QtWidgets.QMessageBox.warning(
            None,
            "Database Error",
            f"A database operation failed while loading local zone or aggregate date range zone data.\n\nDetails:\n{str(e)}"
        )
        raise

    except ValueError as e:
        logging.exception("Configuration error while loading local zone data")
        QtWidgets.QMessageBox.warning(
            None,
            "Configuration Error",
            f"Invalid database connection or missing required input while preparing zone data.\n\nDetails:\n{str(e)}"
        )
        raise

    except RuntimeError as e:
        logging.exception("Data integrity error while loading local zone data")
        QtWidgets.QMessageBox.warning(
            None,
            "Data Integrity Error",
            f"Critical zone or aggregate date range zone data was missing or inconsistent during the load process.\n\nDetails:\n{str(e)}"
        )
        raise

    except Exception as e:
        logging.exception("Unhandled error while loading local zone data")
        QtWidgets.QMessageBox.warning(
            None,
            "Unexpected Error",
            f"An unexpected failure occurred while loading zone data.\n\nDetails:\n{str(e)}"
        )
        raise