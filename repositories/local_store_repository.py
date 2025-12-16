"""Database query functions for retrieving store data."""
import pyodbc

from models import InventoryTable


def fetch_old_inventory_data(conn: pyodbc.Connection, store: str) -> pyodbc.Row | None:
    """Fetch inventory data from the local database.

    Args:
        conn: Database connection object
        store: Store number inputted by user

    Returns:
        Pyodbc row containing inventory data
    """
    cursor = conn.cursor()
    inventory = InventoryTable()

    inventory_query = f"""
        SELECT
            {inventory.table}.{inventory.job_datetime},
            {inventory.table}.{inventory.store_name},
            {inventory.table}.{inventory.store_address}
        FROM {inventory.table}
        WHERE {inventory.table}.{inventory.store_number} = ?
    """
    cursor.execute(inventory_query, (store,))
    inventory_row = cursor.fetchone()

    cursor.close()
    return inventory_row


def fetch_season_inventory_data(conn: pyodbc.Connection) -> list[pyodbc.Row] | None:
    """Fetch inventory data from the local database for the season.

    Args:
        conn: Database connection object

    Returns:
        List of pyodbc rows containing season inventory data
    """
    cursor = conn.cursor()
    inventory = InventoryTable()

    inventory_query = f"""
        SELECT {inventory.table}.{inventory.job_datetime}
        FROM {inventory.table}
        WHERE YEAR({inventory.table}.{inventory.job_datetime}) = YEAR(Date())
    """
    cursor.execute(inventory_query)
    inventory_rows = cursor.fetchall()

    cursor.close()
    return inventory_rows