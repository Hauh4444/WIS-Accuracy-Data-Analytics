"""Saves accuracy report data locally for future retrieval and season accuracy reports."""
import pyodbc
from PyQt6 import QtWidgets

from repositories.save_local_data_repository import (
    create_tables_if_not_exists, check_inventory_exists, check_employee_totals_exist, check_zone_totals_exist, insert_inventory_data, insert_employee_data,
    insert_zone_data, insert_employee_totals_data, insert_zone_totals_data, update_employee_data, update_zone_data, update_employee_totals_data, update_zone_totals_data
)


def save_local_data(conn: pyodbc.Connection, store_data: dict, emp_data: list[dict], team_data: list[dict]) -> None:
    """Save inventory and accuracy report data.

    Args:
        conn: Database connection object
        store_data: Dictionary containing store data
        emp_data: List of employee data dictionaries
        team_data: List of team data dictionaries

    Raises:
        ValueError: If connection is invalid or database schema is malformed
        RuntimeError: If critical employee data is missing or corrupted
    """
    try:
        if conn is None:
            raise ValueError("Database connection cannot be None")
        if not hasattr(conn, 'cursor'):
            raise ValueError("Invalid database connection object - missing cursor method")

        create_tables_if_not_exists(conn=conn)

        store_data["store_number"] = store_data["store"].strip().split()[-1]

        inventory_exists = check_inventory_exists(conn, store_data)
        if not inventory_exists:
            insert_inventory_data(conn, store_data)

        for emp in emp_data:
            employee_totals_exist = check_employee_totals_exist(conn, emp)
            if not employee_totals_exist:
                insert_employee_totals_data(conn, emp)

            if inventory_exists:
                prev_emp_data = update_employee_data(conn, store_data, emp)
            else:
                insert_employee_data(conn, store_data, emp)
                prev_emp_data = None

            if employee_totals_exist:
                update_employee_totals_data(conn, prev_emp_data, emp)

        for zone in team_data:
            zone_totals_exist = check_zone_totals_exist(conn, zone)
            if not zone_totals_exist:
                insert_zone_totals_data(conn, zone)

            if inventory_exists:
                prev_zone_data = update_zone_data(conn, store_data, zone)
            else:
                insert_zone_data(conn, store_data, zone)
                prev_zone_data = None

            if zone_totals_exist:
                update_zone_totals_data(conn, prev_zone_data, zone)

    except (pyodbc.Error, pyodbc.DatabaseError) as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Database Error",
            f"A database operation failed while saving local data.\n\nDetails:\n{str(e)}"
        )
        raise

    except ValueError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Configuration Error",
            f"Invalid configuration or missing required input while preparing local data.\n\nDetails:\n{str(e)}"
        )
        raise

    except RuntimeError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Data Integrity Error",
            f"Critical employee or zone data was missing or inconsistent during the save process.\n\nDetails:\n{str(e)}"
        )
        raise

    except Exception as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Unexpected Error",
            f"An unexpected failure occurred while saving local data.\nThis may indicate corrupt input, missing fields, or an unhandled edge case.\n\nDetails:\n{str(e)}"
        )
        raise