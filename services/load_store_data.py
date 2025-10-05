import pyodbc
from PyQt6 import QtWidgets
from datetime import datetime

from services.models import WISEInfoTable


def load_store_data(conn: pyodbc.Connection) -> dict:
    """Load store data with from the database.

    Args:
        conn: Database connection object

    Returns:
        Dictionary containing store information for report page headers
    """
    try:
        cursor = conn.cursor()

        wise = WISEInfoTable()

        zone_query = f"""
            SELECT TOP 1
                {wise.table}.{wise.job_datetime},
                {wise.table}.{wise.name},
                {wise.table}.{wise.address}
            FROM {wise.table}
        """
        cursor.execute(zone_query)
        wise_row = cursor.fetchone()

        if wise_row is None:
            raise Exception("No WISE data found in database - tblWISEInfo table is empty")

        now = datetime.now()

        return {
            "inventory_datetime": wise_row[0],
            "print_date": f"{now.month}/{now.day}/{now.year}",
            "store": wise_row[1],
            "print_time": now.strftime("%I:%M:%S%p"),
            "store_address": wise_row[2]
        }
    except Exception as e:
        try:
            QtWidgets.QMessageBox.critical(None, "Database Error", f"Failed to load store data: {str(e)}")
        except:
            pass

        now = datetime.now()

        return {
            "inventory_datetime": "",
            "print_date": f"{now.month}/{now.day}/{now.year}",
            "store": "",
            "print_time": now.strftime("%I:%M:%S%p"),
            "store_address": ""
        }