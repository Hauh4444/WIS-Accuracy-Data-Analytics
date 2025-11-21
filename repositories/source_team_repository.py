"""Database query functions for retrieving team data."""
import pyodbc

from source_models import ZoneTable, ZoneChangeQueueTable, ZoneChangeInfoTable, TagRangeTable


def fetch_zone_data(conn: pyodbc.Connection) -> list[pyodbc.Row] | None:
    """Fetch zone data from the database.

    Args:
        conn: Database connection object

    Returns:
        List of pyodbc rows containing zone data
    """
    cursor = conn.cursor()
    zone = ZoneTable()

    zone_query = f"""
        SELECT DISTINCT
            {zone.table}.{zone.zone_id},
            {zone.table}.{zone.zone_description}
        FROM {zone.table}
        ORDER BY {zone.table}.{zone.zone_id}
    """
    cursor.execute(zone_query)
    zone_rows = cursor.fetchall()

    cursor.close()
    return zone_rows


def fetch_zone_totals_data(conn: pyodbc.Connection, zone_id: str) -> pyodbc.Row | None:
    """Fetch zone totals data from the database.

    Args:
        conn: Database connection object
        zone_id: The zone id to match

    Returns:
        List of pyodbc rows containing zone totals data
    """
    cursor = conn.cursor()
    tag_range = TagRangeTable()

    zone_totals_query = f"""
        SELECT 
            Sum({tag_range.table}.{tag_range.tag_val_to} - {tag_range.table}.{tag_range.tag_val_from} + 1),
            Sum({tag_range.table}.{tag_range.total_quantity}),
            Sum({tag_range.table}.{tag_range.total_price})
        FROM {tag_range.table}
        WHERE {tag_range.table}.{tag_range.zone_id} = ?
    """
    cursor.execute(zone_totals_query, (zone_id,))
    zone_totals_row = cursor.fetchone()

    cursor.close()
    return zone_totals_row


def fetch_zone_discrepancy_totals_data(conn: pyodbc.Connection, zone_id: str) -> pyodbc.Row | None:
    """Fetch zone discrepancy totals data from the database.

    Args:
        conn: Database connection object
        zone_id: The zone id to match

    Returns:
        List of pyodbc rows containing zone discrepancy totals data
    """
    cursor = conn.cursor()
    queue = ZoneChangeQueueTable()
    info = ZoneChangeInfoTable()

    zone_discrepancy_totals_query = f"""
        SELECT 
            Sum(Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.quantity}))),
            (
                SELECT Count(*)
                FROM (
                    SELECT DISTINCT {queue.table}.{queue.tag_number}
                    FROM {queue.table}
                    INNER JOIN {info.table} ON {queue.table}.{queue.zone_queue_id} = {info.table}.{info.zone_queue_id}
                    WHERE {queue.table}.{queue.reason} = 'SERVICE_MISCOUNTED'
                        AND {queue.table}.{queue.zone_id} = ?
                        AND Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.quantity})) > 50
                )
            )
        FROM {queue.table}
        INNER JOIN {info.table} ON {queue.table}.{queue.zone_queue_id} = {info.table}.{info.zone_queue_id}
        WHERE {queue.table}.{queue.reason} = 'SERVICE_MISCOUNTED'
            AND {queue.table}.{queue.zone_id} = ?
            AND Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.quantity})) > 50
    """
    cursor.execute(zone_discrepancy_totals_query, (zone_id, zone_id))
    zone_discrepancy_totals_row = cursor.fetchone()

    cursor.close()
    return zone_discrepancy_totals_row