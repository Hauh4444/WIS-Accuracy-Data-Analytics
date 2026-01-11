"""Saves accuracy report data locally for future retrieval and season accuracy reports."""
import pyodbc
import logging
from PyQt6 import QtWidgets

from repositories import (
    create_tables_if_not_exists, check_inventory_exists, check_employee_totals_exist, check_zone_totals_exist, insert_inventory_data, insert_employee_data,
    insert_zone_data, insert_employee_totals_data, insert_zone_totals_data, update_employee_data, update_zone_data, update_employee_totals_data, update_zone_totals_data
)


# TODO: Need to store discrepancies
def save_local_data(conn: pyodbc.Connection, store_data: dict, emp_data: list[dict], zone_data: list[dict]) -> None:
    """Save inventory and accuracy report data.

    Args:
        conn: Database connection object
        store_data: Dictionary containing store data
        emp_data: List of employee data dictionaries
        zone_data: List of zone data dictionaries

    Raises:
        ValueError: If connection is invalid or database schema is malformed
        RuntimeError: If critical employee data is missing or corrupted
    """
    try:
        if conn is None:
            raise ValueError("Database connection cannot be None")
        if not hasattr(conn, 'cursor'):
            raise ValueError("Invalid database connection object - missing cursor method")

        create_tables_if_not_exists(conn)

        store_data["store_number"] = store_data["store"].strip().split()[-1]

        if check_inventory_exists(conn, store_data):
            handle_employee = update_employee_data
            handle_zone = update_zone_data
        else:
            insert_inventory_data(conn, store_data)
            handle_employee = insert_employee_data
            handle_zone = insert_zone_data

        for emp in emp_data:
            handle_employee(conn, store_data, emp)

        for zone in zone_data:
            handle_zone(conn, store_data, zone)

    except (pyodbc.Error, pyodbc.DatabaseError) as e:
        logging.exception("Database error while saving local data")
        QtWidgets.QMessageBox.warning(
            None,
            "Database Error",
            f"A database operation failed while saving local data.\n\nDetails:\n{str(e)}"
        )
        raise

    except ValueError as e:
        logging.exception("Configuration error while saving local data")
        QtWidgets.QMessageBox.warning(
            None,
            "Configuration Error",
            f"Invalid configuration or missing required input while preparing local data.\n\nDetails:\n{str(e)}"
        )
        raise

    except RuntimeError as e:
        logging.exception("Data integrity error while saving local data")
        QtWidgets.QMessageBox.warning(
            None,
            "Data Integrity Error",
            f"Critical employee or zone data was missing or inconsistent during the save process.\n\nDetails:\n{str(e)}"
        )
        raise

    except Exception as e:
        logging.exception("Unhandled error while saving local data")
        QtWidgets.QMessageBox.warning(
            None,
            "Unexpected Error",
            f"An unexpected failure occurred while saving local data.\n\nDetails:\n{str(e)}"
        )
        raise