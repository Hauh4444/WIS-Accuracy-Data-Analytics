"""Database query functions for retrieving discrepancy data."""
import pyodbc

from models import DiscrepancyTable


def fetch_historical_discrepancy_data(conn: pyodbc.Connection, store: str, emp_number: str) -> list[pyodbc.Row] | None:
    """Fetch discrepancy data from the database for a given store and employee.

    Args:
        conn: Database connection object
        store: Store number inputted by user
        emp_number: Employee number to fetch discrepancies for

    Returns:
        List of pyodbc rows containing discrepancy data for a given store and employee
    """
    cursor = conn.cursor()
    disc = DiscrepancyTable()

    disc_query = f"""
        SELECT DISTINCT 
            {disc.table}.{disc.zone_id},
            {disc.table}.{disc.tag_number},
            {disc.table}.{disc.upc},
            {disc.table}.{disc.price},
            {disc.table}.{disc.counted_quantity},
            {disc.table}.{disc.new_quantity},
            {disc.table}.{disc.price_change}
        FROM {disc.table}
        WHERE {disc.table}.{disc.store_number} = ? AND {disc.table}.{disc.emp_number} = ?
    """
    cursor.execute(disc_query, (store, emp_number))
    disc_rows = cursor.fetchall()

    cursor.close()
    return disc_rows