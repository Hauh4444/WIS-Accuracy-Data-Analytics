"""Database query functions for retrieving employee data."""
import pyodbc

from models.local_models import EmployeeTable, EmployeeTotalsTable


def fetch_emp_data(conn: pyodbc.Connection, store: str) -> list[pyodbc.Row] | None:
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


def fetch_season_emp_data(conn: pyodbc.Connection) -> list[pyodbc.Row] | None:
    """Fetch employee data from the database for the season.

    Args:
        conn: Database connection object

    Returns:
        List of pyodbc rows containing season employee data
    """
    cursor = conn.cursor()
    emp_totals = EmployeeTotalsTable()

    emp_totals_query = f"""
        SELECT DISTINCT 
            {emp_totals.table}.{emp_totals.emp_number},
            {emp_totals.table}.{emp_totals.emp_name},
            {emp_totals.table}.{emp_totals.total_tags},
            {emp_totals.table}.{emp_totals.total_quantity},
            {emp_totals.table}.{emp_totals.total_price},
            {emp_totals.table}.{emp_totals.discrepancy_dollars},
            {emp_totals.table}.{emp_totals.discrepancy_tags},
            {emp_totals.table}.{emp_totals.stores},
            {emp_totals.table}.{emp_totals.hours}
        FROM {emp_totals.table}
    """
    cursor.execute(emp_totals_query)
    emp_totals_rows = cursor.fetchall()

    cursor.close()
    return emp_totals_rows