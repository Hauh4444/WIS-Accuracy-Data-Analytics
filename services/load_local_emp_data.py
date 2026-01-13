"""Employee data loader with inventory accuracy metrics."""
import pyodbc
import logging
from PyQt6 import QtWidgets
from datetime import datetime

from repositories import fetch_historical_emp_data, fetch_historical_discrepancy_data, fetch_aggregate_emp_data


def load_local_emp_data(conn: pyodbc.Connection, store: str | None, date_range: list[datetime] | None = None) -> list[dict] | None:
    """Load employee data with discrepancy calculations.

    Args:
        conn: Database connection object
        store: Store number inputted by user or None if retrieving range stats
        date_range: Range of datetimes inputted by user or None if retrieving store stats

    Returns:
        List of dictionaries containing employee data with totals and discrepancies

    Raises:
        ValueError: If connection is invalid or database schema is malformed
        RuntimeError: If critical employee data is missing or corrupted
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
            emp_rows = fetch_historical_emp_data(conn, store)
        else:
            emp_rows = fetch_aggregate_emp_data(conn, date_range)

        emp_data: list[dict] = []

        for emp_row in emp_rows:
            emp_data_row = {
                "emp_number": emp_row[0] or "",
                "emp_name": emp_row[1] or "",
                "total_tags": emp_row[2] or 0,
                "total_quantity": emp_row[3] or 0,
                "total_price": emp_row[4] or 0.0,
                "discrepancy_dollars": emp_row[5] or 0.0,
                "discrepancy_tags": emp_row[6] or 0,
                "discrepancies": [],
                "hours": emp_row[7] or 0,
                "stores": (emp_row[8] or 1) if date_range else None,
            }
            emp_data_row["uph"] = emp_data_row["total_quantity"] / emp_data_row["hours"] if emp_data_row["total_quantity"] and emp_data_row["hours"] else 0
            emp_data_row["discrepancy_percent"] = (emp_data_row["discrepancy_dollars"] / emp_data_row["total_price"] * 100) if emp_data_row["total_price"] > 0 else 0

            if not store:
                emp_data.append(emp_data_row)
                continue

            emp_discrepancies_rows = fetch_historical_discrepancy_data(conn, store, emp_data_row["emp_number"])
            for emp_discrepancies_row in emp_discrepancies_rows:
                discrepancy_row: dict = {
                    "zone_id": emp_discrepancies_row[0] or "",
                    "tag_number": emp_discrepancies_row[1] or "",
                    "upc": emp_discrepancies_row[2] or "",
                    "counted_quantity": emp_discrepancies_row[3] or 0,
                    "new_quantity": emp_discrepancies_row[4] or 0,
                    "price": emp_discrepancies_row[5] or 0.0,
                    "price_change": emp_discrepancies_row[6] or 0.0
                }
                emp_data_row["discrepancies"].append(discrepancy_row)
            emp_data.append(emp_data_row)

        return emp_data

    except (pyodbc.Error, pyodbc.DatabaseError) as e:
        logging.exception("Database error while loading local employee data")
        QtWidgets.QMessageBox.warning(
            None,
            "Database Error",
            f"A database operation failed while loading local local or aggregate date range employee data.\n\nDetails:\n{str(e)}"
        )
        raise

    except ValueError as e:
        logging.exception("Configuration error while loading local employee data")
        QtWidgets.QMessageBox.warning(
            None,
            "Configuration Error",
            f"Invalid database connection or missing required input while preparing employee data.\n\nDetails:\n{str(e)}"
        )
        raise

    except RuntimeError as e:
        logging.exception("Data integrity error while loading local employee data")
        QtWidgets.QMessageBox.warning(
            None,
            "Data Integrity Error",
            f"Critical employee data was missing or inconsistent during the load process.\n\nDetails:\n{str(e)}"
        )
        raise

    except Exception as e:
        logging.exception("Unhandled error while loading local employee data")
        QtWidgets.QMessageBox.warning(
            None,
            "Unexpected Error",
            f"An unexpected failure occurred while loading local employee data.\n\nDetails:\n{str(e)}"
        )
        raise