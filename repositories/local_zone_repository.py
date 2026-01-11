"""Database query functions for retrieving zone data."""
import pyodbc
from datetime import datetime

from models import ZoneTable, InventoryTable


def fetch_old_zone_data(conn: pyodbc.Connection, store: str) -> list[pyodbc.Row] | None:
    """Fetch zone data from the database for a given store.

    Args:
        conn: Database connection object
        store: Store number inputted by user

    Returns:
        List of pyodbc rows containing zone data for a given store.
    """
    cursor = conn.cursor()
    zone = ZoneTable()

    zone_query = f"""
        SELECT DISTINCT
            {zone.table}.{zone.zone_id},
            {zone.table}.{zone.zone_description},
            {zone.table}.{zone.total_tags},
            {zone.table}.{zone.total_quantity},
            {zone.table}.{zone.total_price},
            {zone.table}.{zone.discrepancy_dollars},
            {zone.table}.{zone.discrepancy_tags}
        FROM {zone.table}
        WHERE {zone.table}.{zone.store_number} = ?
    """
    cursor.execute(zone_query, (store,))
    zone_rows = cursor.fetchall()

    cursor.close()
    return zone_rows


def fetch_range_zone_data(conn: pyodbc.Connection, date_range: list[datetime]) -> list[pyodbc.Row] | None:
    """Fetch zone data from the database for a range of dates.

    Args:
        conn: Database connection object
        date_range: Range of datetimes inputted by user or None if retrieving store stats

    Returns:
        List of pyodbc rows containing range zone data.
    """
    cursor = conn.cursor()
    zone = ZoneTable()
    inventory = InventoryTable()

    query = f"""
        SELECT
            z.{zone.zone_id},
            FIRST(z.{zone.zone_description}) AS {zone.zone_description},
            AVG(z.{zone.total_tags}) AS {zone.total_tags},
            AVG(z.{zone.total_quantity}) AS {zone.total_quantity},
            AVG(z.{zone.total_price}) AS {zone.total_price},
            AVG(z.{zone.discrepancy_dollars}) AS {zone.discrepancy_dollars},
            AVG(z.{zone.discrepancy_tags}) AS {zone.discrepancy_tags},
            COUNT(*) AS TotalStores
        FROM {zone.table} AS z
        INNER JOIN {inventory.table} AS i
            ON z.{zone.store_number} = i.{inventory.store_number}
        WHERE
            CDate(i.{inventory.job_datetime}) BETWEEN ? AND ?
        GROUP BY
            z.{zone.zone_id}
    """

    cursor.execute(query, (date_range[0], date_range[1]))
    zone_totals_rows = cursor.fetchall()

    cursor.close()
    return zone_totals_rows
