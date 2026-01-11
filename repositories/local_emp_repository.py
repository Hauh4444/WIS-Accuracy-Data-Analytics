"""Database query functions for retrieving employee data."""
import pyodbc
from datetime import datetime

from models import EmployeeTable, InventoryTable


def fetch_old_emp_data(conn: pyodbc.Connection, store: str) -> list[pyodbc.Row] | None:
    """Fetch employee data from the database for a given store.

    Args:
        conn: Database connection object
        store: Store number inputted by user

    Returns:
        List of pyodbc rows containing employee data for a given store
    """
    cursor = conn.cursor()
    emp = EmployeeTable()

    emp_query = f"""
        SELECT DISTINCT 
            {emp.table}.{emp.emp_number},
            {emp.table}.{emp.emp_name},
            {emp.table}.{emp.total_tags},
            {emp.table}.{emp.total_quantity},
            {emp.table}.{emp.total_price},
            {emp.table}.{emp.discrepancy_dollars},
            {emp.table}.{emp.discrepancy_tags},
            {emp.table}.{emp.hours}
        FROM {emp.table}
        WHERE {emp.table}.{emp.store_number} = ?
    """
    cursor.execute(emp_query, (store,))
    emp_rows = cursor.fetchall()

    cursor.close()
    return emp_rows


def fetch_range_emp_data(conn: pyodbc.Connection, date_range: list[datetime]) -> list[pyodbc.Row] | None:
    """Fetch employee data from the database for a range of dates.

    Args:
        conn: Database connection object
        date_range: Range of datetimes inputted by user or None if retrieving store stats

    Returns:
        List of pyodbc rows containing range employee data
    """
    cursor = conn.cursor()
    emp = EmployeeTable()
    inventory = InventoryTable()

    query = f"""
        SELECT
            e.{emp.emp_number},
            FIRST(e.{emp.emp_name}) AS {emp.emp_name},
            AVG(e.{emp.total_tags}) AS {emp.total_tags},
            AVG(e.{emp.total_quantity}) AS {emp.total_quantity},
            AVG(e.{emp.total_price}) AS {emp.total_price},
            AVG(e.{emp.discrepancy_dollars}) AS {emp.discrepancy_dollars},
            AVG(e.{emp.discrepancy_tags}) AS {emp.discrepancy_tags},
            AVG(e.{emp.hours}) AS {emp.hours},
            COUNT(*) AS TotalStores
        FROM {emp.table} AS e
        INNER JOIN {inventory.table} AS i
            ON e.{emp.store_number} = i.{inventory.store_number}
        WHERE
            CDate(i.{inventory.job_datetime}) BETWEEN ? AND ?
        GROUP BY
            e.{emp.emp_number}
    """

    cursor.execute(query, (date_range[0], date_range[1]))
    rows = cursor.fetchall()
    cursor.close()

    return rows