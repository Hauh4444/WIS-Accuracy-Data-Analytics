"""Database query functions for retrieving store data."""
import pyodbc

from source_models import WISEInfoTable


def fetch_wise_data(conn: pyodbc.Connection) -> pyodbc.Row | None:
    """Fetch wise data from the database.

    Args:
        conn: Database connection object

    Returns:
        Pyodbc row containing wise data
    """
    cursor = conn.cursor()
    wise = WISEInfoTable()

    wise_query = f"""
        SELECT
            {wise.table}.{wise.job_datetime},
            {wise.table}.{wise.name},
            {wise.table}.{wise.address}
        FROM {wise.table}
    """
    cursor.execute(wise_query)
    wise_row = cursor.fetchone()

    cursor.close()
    return wise_row