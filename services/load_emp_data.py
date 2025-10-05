import pyodbc
from PyQt6 import QtWidgets

from services.models import UPHTable, DetailsTable, ZoneChangeQueueTable, ZoneChangeInfoTable, TagTable


def load_emp_data(conn: pyodbc.Connection) -> list[dict]:
    """Load employee data with discrepancy calculations from the database.
    
    Args:
        conn: Database connection object
        
    Returns:
        List of dictionaries containing employee data with totals and discrepancies
    """
    result = []
    
    try:
        cursor = conn.cursor()

        uph = UPHTable()
        details = DetailsTable()
        queue = ZoneChangeQueueTable()
        info = ZoneChangeInfoTable()
        tag = TagTable()

        emp_query = f"""
            SELECT 
                {uph.table}.{uph.emp_no},
                {uph.table}.{uph.emp_name},
                {uph.table}.{uph.tag_count}
            FROM {uph.table}
            WHERE {uph.table}.{uph.emp_no} != 'ZZ9999'
            ORDER BY {uph.table}.{uph.emp_no}
        """
        cursor.execute(emp_query)
        emp_rows = cursor.fetchall()
        
        for emp_row in emp_rows:
            emp_no = emp_row[0]
            emp_name = emp_row[1]
            tag_count = emp_row[2]
            
            tags_query = f"""
                SELECT DISTINCT {details.table}.{details.tag}
                FROM {details.table}
                WHERE {details.table}.{details.emp_no} = '{emp_no}'
            """
            cursor.execute(tags_query)
            tag_rows = cursor.fetchall()
            
            total_quantity = 0
            total_price = 0
            
            for tag_row in tag_rows:
                tag_value = tag_row[0]

                tag_totals_query = f"""
                    SELECT 
                        {tag.table}.{tag.total_qty},
                        {tag.table}.{tag.total_ext}
                    FROM {tag.table}
                    WHERE CInt({tag.table}.{tag.tag_no}) = CInt({tag_value})
                """
                cursor.execute(tag_totals_query)
                tag_totals_row = cursor.fetchone()
                
                if tag_totals_row:
                    total_quantity += tag_totals_row[0] if tag_totals_row[0] is not None else 0
                    total_price += tag_totals_row[1] if tag_totals_row[1] is not None else 0
            
            employee_tags = [str(tag_row[0]) for tag_row in tag_rows]
            tags_filter = ','.join(employee_tags) if employee_tags else "''"
            
            discrepancy_dollars_query = f"""
                SELECT 
                    Sum(
                        Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.counted_qty}))
                    ) AS discrepancy_dollars
                FROM {queue.table}
                INNER JOIN {info.table} ON {queue.table}.{queue.zone_queue_id} = {info.table}.{info.zone_queue_id}
                WHERE {queue.table}.{queue.reason} = 'SERVICE_MISCOUNTED'
                    AND CInt({queue.table}.{queue.tag}) IN ({tags_filter})
                    AND Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.counted_qty})) > 50
            """
            
            discrepancy_tags_query = f"""
                SELECT Count(*) AS discrepancy_tags
                FROM (
                    SELECT DISTINCT {queue.table}.{queue.tag}
                    FROM {queue.table}
                    INNER JOIN {info.table} ON {queue.table}.{queue.zone_queue_id} = {info.table}.{info.zone_queue_id}
                    WHERE {queue.table}.{queue.reason} = 'SERVICE_MISCOUNTED'
                        AND CInt({queue.table}.{queue.tag}) IN ({tags_filter})
                        AND Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.counted_qty})) > 50
                )
            """
            cursor.execute(discrepancy_dollars_query)
            discrepancy_dollars_row = cursor.fetchone()
            discrepancy_dollars = discrepancy_dollars_row[0] if discrepancy_dollars_row and discrepancy_dollars_row[0] is not None else 0
            
            cursor.execute(discrepancy_tags_query)
            discrepancy_tags_row = cursor.fetchone()
            discrepancy_tags = discrepancy_tags_row[0] if discrepancy_tags_row and discrepancy_tags_row[0] is not None else 0
            discrepancy_percent = (discrepancy_dollars / total_price * 100) if total_price > 0 else 0
            
            result.append({
                'employee_id': emp_no,
                'employee_name': emp_name,
                'total_tags': tag_count,
                'total_quantity': total_quantity,
                'total_price': total_price,
                'total_discrepancy_dollars': discrepancy_dollars,
                'total_discrepancy_tags': discrepancy_tags,
                'discrepancy_percent': discrepancy_percent
            })
            
        return result
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Database Error", f"Failed to load employee data: {str(e)}")
        return []