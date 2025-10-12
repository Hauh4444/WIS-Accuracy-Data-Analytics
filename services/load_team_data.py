"""Team/zone data loader with inventory accuracy metrics."""
import pyodbc
from PyQt6 import QtWidgets

from services.models import ZoneTable, ZoneChangeQueueTable, ZoneChangeInfoTable, TagRangeTable


def load_team_data(conn: pyodbc.Connection) -> list[dict]:
    """Load team/zone data with discrepancy calculations.
    
    Business rule: Only discrepancies >$50 with reason='SERVICE_MISCOUNTED' are counted against the team.
    
    Args:
        conn: Database connection object
        
    Returns:
        List of dictionaries containing team data with totals and discrepancies
    """
    team_data = []
    
    try:
        cursor = conn.cursor()
        zone = ZoneTable()
        queue = ZoneChangeQueueTable()
        info = ZoneChangeInfoTable()
        tag_range = TagRangeTable()

        zone_query = f"""
            SELECT 
                {zone.table}.{zone.zone_id},
                {zone.table}.{zone.zone_desc}
            FROM {zone.table}
            ORDER BY {zone.table}.{zone.zone_id}
        """
        cursor.execute(zone_query)
        zone_rows = cursor.fetchall()
        
        for zone_row in zone_rows:
            zone_id = zone_row[0] if zone_row and zone_row[0] else ""
            zone_desc = zone_row[1] if zone_row and zone_row[1] else ""

            zone_totals_query = f"""
                SELECT 
                    Sum({tag_range.table}.{tag_range.tag_val_to} - {tag_range.table}.{tag_range.tag_val_from} + 1),
                    Sum({tag_range.table}.{tag_range.total_qty}),
                    Sum({tag_range.table}.{tag_range.total_ext})
                FROM {tag_range.table}
                WHERE {tag_range.table}.{tag_range.zone_id} = ?
            """
            cursor.execute(zone_totals_query, (zone_id,))
            zone_totals_row = cursor.fetchone()
            
            total_tags = zone_totals_row[0] if zone_totals_row and zone_totals_row[0] is not None else 0
            total_quantity = zone_totals_row[1] if zone_totals_row and zone_totals_row[1] is not None else 0
            total_price = zone_totals_row[2] if zone_totals_row and zone_totals_row[2] is not None else 0

            discrepancy_dollars_query = f"""
                SELECT Sum(Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.counted_qty})))
                FROM {queue.table}
                INNER JOIN {info.table} ON {queue.table}.{queue.zone_queue_id} = {info.table}.{info.zone_queue_id}
                WHERE {queue.table}.{queue.reason} = 'SERVICE_MISCOUNTED'
                    AND {queue.table}.{queue.zone_id} = ?
                    AND Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.counted_qty})) > 50
            """
            cursor.execute(discrepancy_dollars_query, (zone_id,))
            discrepancy_dollars_row = cursor.fetchone()
            discrepancy_dollars = discrepancy_dollars_row[0] if discrepancy_dollars_row and discrepancy_dollars_row[0] is not None else 0

            discrepancy_tags_query = f"""
                SELECT DISTINCT {queue.table}.{queue.tag}
                FROM {queue.table}
                INNER JOIN {info.table} ON {queue.table}.{queue.zone_queue_id} = {info.table}.{info.zone_queue_id}
                WHERE {queue.table}.{queue.reason} = 'SERVICE_MISCOUNTED'
                    AND {queue.table}.{queue.zone_id} = ?
                    AND Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.counted_qty})) > 50
            """
            cursor.execute(discrepancy_tags_query, (zone_id,))
            discrepancy_tags_rows = cursor.fetchall()
            discrepancy_tags = len(discrepancy_tags_rows)
            discrepancy_percent = (discrepancy_dollars / total_price * 100) if total_price > 0 else 0
            
            team_data.append({
                'department_number': zone_id,
                'department_name': zone_desc,
                'total_tags': total_tags,
                'total_quantity': total_quantity,
                'total_price': total_price,
                'total_discrepancy_dollars': discrepancy_dollars,
                'total_discrepancy_tags': discrepancy_tags,
                'discrepancy_percent': discrepancy_percent
            })
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Database Error", f"Failed to load team data: {str(e)}")

    return team_data