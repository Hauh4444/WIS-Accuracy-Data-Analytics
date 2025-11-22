"""Store metadata loader for report headers."""
from datetime import datetime

import pyodbc
from PyQt6 import QtWidgets

from repositories.local_store_repository import fetch_inventory_data


def load_local_store_data(conn: pyodbc.Connection, store: str) -> dict:
    """Load store data for use in report headers.

    Args:
        conn: Database connection object
        store: Store number inputted by user

    Returns:
        Dictionary containing store information for report page headers

    Raises:
        ValueError: If connection is invalid or database schema is malformed
        RuntimeError: If critical store data is missing or corrupted
    """
    now = datetime.now()
    store_data = {
        "inventory_datetime": "",
        "print_date": f"{now.month}/{now.day}/{now.year}",
        "store": "",
        "print_time": now.strftime("%I:%M:%S%p"),
        "store_address": ""
    }

    if conn is None:
        raise ValueError("Database connection cannot be None")
    if not hasattr(conn, 'cursor'):
        raise ValueError("Invalid database connection object - missing cursor method")

    cursor = conn.cursor()
    cursor.execute("select * from tblInventory")
    print(cursor.fetchall())
    cursor.execute("select * from tblEmps")
    emps = cursor.fetchall()
    for emp in emps:
        print(emp)
    print("--------------------------------------------")
    cursor.execute("select * from tblEmpTotals")
    emps = cursor.fetchall()
    for emp in emps:
        print(emp)

    inventory_row = fetch_inventory_data(conn=conn, store=store)
    if inventory_row is None or len(inventory_row) != 3:
        raise RuntimeError(
            f"Unexpected Inventory data structure - expected 3 columns, got {len(inventory_row) if inventory_row else None}")

    store_data["inventory_datetime"] = inventory_row[0] if inventory_row[0] is not None else ""
    store_data["store"] = inventory_row[1] if inventory_row[1] is not None else ""
    store_data["store_address"] = inventory_row[2] if inventory_row[2] is not None else ""

    return store_data