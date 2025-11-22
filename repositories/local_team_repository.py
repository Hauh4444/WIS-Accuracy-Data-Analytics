"""Database query functions for retrieving team data."""
import pyodbc

from models.local_models import ZoneTable, ZoneTotalsTable


def fetch_zone_data(conn: pyodbc.Connection, store: str) -> list[pyodbc.Row] | None:
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


def fetch_season_zone_data(conn: pyodbc.Connection) -> list[pyodbc.Row] | None:
    """Fetch zone data from the database for the season.

    Args:
        conn: Database connection object

    Returns:
        List of pyodbc rows containing season zone data.
    """
    cursor = conn.cursor()
    zone_totals = ZoneTotalsTable()

    zone_totals_query = f"""
        SELECT DISTINCT
            {zone_totals.table}.{zone_totals.zone_id},
            {zone_totals.table}.{zone_totals.zone_description},
            {zone_totals.table}.{zone_totals.total_tags},
            {zone_totals.table}.{zone_totals.total_quantity},
            {zone_totals.table}.{zone_totals.total_price},
            {zone_totals.table}.{zone_totals.discrepancy_dollars},
            {zone_totals.table}.{zone_totals.discrepancy_tags},
            {zone_totals.table}.{zone_totals.stores}
        FROM {zone_totals.table}
    """
    cursor.execute(zone_totals_query)
    zone_totals_rows = cursor.fetchall()

    cursor.close()
    return zone_totals_rows
