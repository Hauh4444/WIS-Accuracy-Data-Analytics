"""Team zone data loader with inventory accuracy metrics."""
import pyodbc
from PyQt6 import QtWidgets

from services.models import ZoneTable, ZoneChangeQueueTable, ZoneChangeInfoTable, TagRangeTable


def load_team_data(conn: pyodbc.Connection) -> list[dict]:
    """Load team zone data with discrepancy calculations.
    
    Business rule: Only discrepancies >$50 with reason='SERVICE_MISCOUNTED' are counted against the team.
    
    Args:
        conn: Database connection object
        
    Returns:
        List of dictionaries containing team data with totals and discrepancies
        
    Raises:
        ValueError: If connection is invalid or database schema is malformed
        RuntimeError: If critical team data is missing or corrupted
    """
    team_data = []
    
    try:
        if conn is None:
            raise ValueError("Database connection cannot be None")
        if not hasattr(conn, 'cursor'):
            raise ValueError("Invalid database connection object - missing cursor method")

        cursor = conn.cursor()
        zone = ZoneTable()
        queue = ZoneChangeQueueTable()
        info = ZoneChangeInfoTable()
        tag_range = TagRangeTable()

        zone_query = f"""
            SELECT DISTINCT
                {zone.table}.{zone.zone_id},
                {zone.table}.{zone.zone_description}
            FROM {zone.table}
            ORDER BY {zone.table}.{zone.zone_id}
        """
        cursor.execute(zone_query)
        zone_rows = cursor.fetchall()
        
        for zone_row in zone_rows:
            if len(zone_row) != 2:
                raise RuntimeError(f"Invalid zone query result structure - expected 2 columns, got {len(zone_row) if zone_row else 0}")
            
            zone_id = zone_row[0] if zone_row and zone_row[0] is not None else ""
            zone_description = zone_row[1] if zone_row and zone_row[1] is not None else ""

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
            if zone_totals_row is None or len(zone_totals_row) != 3:
                raise RuntimeError(f"Invalid zone_totals query result - expected 3 columns, got {len(zone_totals_row) if zone_totals_row else 0}")

            total_tags = zone_totals_row[0] if zone_totals_row and zone_totals_row[0] is not None else 0
            total_quantity = zone_totals_row[1] if zone_totals_row and zone_totals_row[1] is not None else 0
            total_price = zone_totals_row[2] if zone_totals_row and zone_totals_row[2] is not None else 0

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
            if zone_discrepancy_totals_row is None or len(zone_discrepancy_totals_row) != 2:
                raise RuntimeError(f"Invalid zone_discrepancy_totals query result - expected 2 columns, got {len(zone_discrepancy_totals_row) if zone_discrepancy_totals_row else 0}")

            discrepancy_dollars = zone_discrepancy_totals_row[0] if zone_discrepancy_totals_row and zone_discrepancy_totals_row[0] is not None else 0
            discrepancy_tags = zone_discrepancy_totals_row[1] if zone_discrepancy_totals_row and zone_discrepancy_totals_row[1] is not None else 0
            discrepancy_percent = (discrepancy_dollars / total_price * 100) if total_price > 0 else 0
            
            team_data.append({
                'zone_number': zone_id,
                'zone_name': zone_description,
                'total_tags': total_tags,
                'total_quantity': total_quantity,
                'total_price': total_price,
                'total_discrepancy_dollars': discrepancy_dollars,
                'total_discrepancy_tags': discrepancy_tags,
                'discrepancy_percent': discrepancy_percent
            })
    except (pyodbc.Error, pyodbc.DatabaseError) as e:
        QtWidgets.QMessageBox.critical(None, "Database Error", f"Database query failed: {str(e)}")
        raise
    except ValueError as e:
        QtWidgets.QMessageBox.critical(None, "Configuration Error", f"Invalid configuration: {str(e)}")
        raise
    except RuntimeError as e:
        QtWidgets.QMessageBox.critical(None, "Data Error", f"Data validation failed: {str(e)}")
        raise
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Unexpected Error", f"An unexpected error occurred: {str(e)}")
        raise

    return team_data