"""Employee data loader with inventory accuracy metrics."""
import pyodbc
from PyQt6 import QtWidgets

from repositories.local_emp_repository import fetch_emp_data, fetch_season_emp_data


def load_local_emp_data(conn: pyodbc.Connection, store: str | None) -> list[dict] | None:
    """Load employee data with discrepancy calculations.

    Args:
        conn: Database connection object
        store: Store number inputted by user or None if retrieving season stats

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

        emp_data = []  # type: list[dict]

        if store:
            emp_rows = fetch_emp_data(conn=conn, store=store)
            for emp_row in emp_rows:
                emp_data_row: dict = {
                    "emp_number": emp_row[0] if emp_row and emp_row[0] else "",
                    "emp_name": emp_row[1] if emp_row and emp_row[1] else "",
                    "total_tags": emp_row[2] if emp_row and emp_row[2] else 0,
                    "total_quantity": emp_row[3] if emp_row and emp_row[3] else 0,
                    "total_price": emp_row[4] if emp_row and emp_row[4] else 0.0,
                    "discrepancy_dollars": emp_row[5] if emp_row and emp_row[5] else 0.0,
                    "discrepancy_tags": emp_row[6] if emp_row and emp_row[6] else 0,
                    "hours": emp_row[7] if emp_row and emp_row[7] else 0
                }
                emp_data_row["discrepancy_percent"] = (emp_data_row["discrepancy_dollars"] / emp_data_row["total_price"] * 100) if emp_data_row["total_price"] > 0 else 0
                emp_data_row["uph"] = emp_data_row["total_quantity"] / emp_data_row["hours"] if emp_data_row["total_price"] > 0 and emp_data_row["hours"] > 0 else 0
                emp_data.append(emp_data_row)
        else:
            emp_totals_rows = fetch_season_emp_data(conn=conn)
            for emp_totals_row in emp_totals_rows:
                emp_data_row: dict = {
                    "emp_number": emp_totals_row[0] if emp_totals_row and emp_totals_row[0] else "",
                    "emp_name": emp_totals_row[1] if emp_totals_row and emp_totals_row[1] else "",
                    "total_tags": emp_totals_row[2] if emp_totals_row and emp_totals_row[2] else 0,
                    "total_quantity": emp_totals_row[3] if emp_totals_row and emp_totals_row[3] else 0,
                    "total_price": emp_totals_row[4] if emp_totals_row and emp_totals_row[4] else 0.0,
                    "discrepancy_dollars": emp_totals_row[5] if emp_totals_row and emp_totals_row[5] else 0.0,
                    "discrepancy_tags": emp_totals_row[6] if emp_totals_row and emp_totals_row[6] else 0,
                    "stores": emp_totals_row[7] if emp_totals_row and emp_totals_row[7] else 0,
                    "hours": emp_totals_row[8] if emp_totals_row and emp_totals_row[8] else 0
                }
                stores = emp_data_row["stores"] or 1
                emp_data_row["uph"] = emp_data_row["total_quantity"] / emp_data_row["hours"] if emp_data_row["total_price"] > 0 and emp_data_row["hours"] > 0 else 0
                emp_data_row["total_tags"] /= stores
                emp_data_row["total_quantity"] /= stores
                emp_data_row["total_price"] /= stores
                emp_data_row["discrepancy_dollars"] /= stores
                emp_data_row["discrepancy_tags"] /= stores
                emp_data_row["hours"] /= stores
                emp_data_row["discrepancy_percent"] = (emp_data_row["discrepancy_dollars"] / emp_data_row["total_price"] * 100) if emp_data_row["total_price"] > 0 else 0
                emp_data.append(emp_data_row)

        return emp_data

    except (pyodbc.Error, pyodbc.DatabaseError) as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Database Error",
            f"A database operation failed while loading local or season employee data.\n\nDetails:\n{str(e)}"
        )
        raise

    except ValueError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Configuration Error",
            f"Invalid database connection or missing required input while preparing employee data.\n\nDetails:\n{str(e)}"
        )
        raise

    except RuntimeError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Data Integrity Error",
            f"Critical employee data was missing or inconsistent during the load process.\n\nDetails:\n{str(e)}"
        )
        raise

    except Exception as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Unexpected Error",
            f"An unexpected failure occurred while loading employee data.\nThis may indicate corrupt input, missing fields, or an unhandled edge case.\n\nDetails:\n{str(e)}"
        )
        raise