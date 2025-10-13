"""Store metadata loader for report headers."""
import pyodbc
from PyQt6 import QtWidgets
from datetime import datetime

from services.models import WISEInfoTable


def load_store_data(conn: pyodbc.Connection) -> dict:
    """Load store data from the database.

    Args:
        conn: Database connection object

    Returns:
        Dictionary containing store information for report page headers
    """
    now = datetime.now()
    store_data = {
        "inventory_datetime": "",
        "print_date": f"{now.month}/{now.day}/{now.year}",
        "store": "",
        "print_time": now.strftime("%I:%M:%S%p"),
        "store_address": ""
    }

    try:
        cursor = conn.cursor()
        wise = WISEInfoTable()

        store_query = f"""
            SELECT
                {wise.table}.{wise.job_datetime},
                {wise.table}.{wise.name},
                {wise.table}.{wise.address}
            FROM {wise.table}
        """
        cursor.execute(store_query)
        wise_row = cursor.fetchone()
        store_data["inventory_datetime"] = wise_row[0] if wise_row and wise_row[0] is not None else ""
        store_data["store"] = wise_row[1] if wise_row and wise_row[1] is not None else ""
        store_data["store_address"] = wise_row[2] if wise_row and wise_row[2] is not None else ""
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Database Error", f"Failed to load store data: {str(e)}")

    return store_data