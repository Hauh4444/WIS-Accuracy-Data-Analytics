import pyodbc
from PyQt6 import QtWidgets

from services.models import UPHTable, DetailsTable, DetailsEditTable, ZoneChangeQueueTable, ZoneChangeInfoTable, TagTable


def load_emp_data(conn: pyodbc.Connection) -> list[dict]:
    """Load employee data with discrepancy calculations from the database.
    
    Args:
        conn: Database connection object
        
    Returns:
        List of dictionaries containing employee data with totals and discrepancies
    """
    uph, details, details_edit, queue, info, tag = UPHTable(), DetailsTable(), DetailsEditTable(), ZoneChangeQueueTable(), ZoneChangeInfoTable(), TagTable()
    
    try:
        emp_query = f"""
        SELECT 
            {uph.table}.{uph.emp_no},
            {uph.table}.{uph.emp_name},
            {uph.table}.{uph.tag_count}
        FROM {uph.table}
        ORDER BY {uph.table}.{uph.emp_no}
        """
        
        cursor = conn.cursor()
        cursor.execute(emp_query)
        emp_rows = cursor.fetchall()
        
        result = []
        
        for emp_row in emp_rows:
            emp_no = emp_row[0]
            emp_name = emp_row[1]
            tag_count = emp_row[2]
            
            tags_query = f"""
            SELECT DISTINCT {details.table}.{details.tag_id}
            FROM {details.table}
            WHERE {details.table}.{details.emp_no} = '{emp_no}'
            """
            
            cursor.execute(tags_query)
            tag_rows = cursor.fetchall()
            
            total_quantity = 0
            total_price = 0
            
            for tag_row in tag_rows:
                tag_id = tag_row[0]
                tag_totals_query = f"""
                SELECT 
                    {tag.table}.{tag.total_qty},
                    {tag.table}.{tag.total_ext}
                FROM {tag.table}
                WHERE CInt({tag.table}.{tag.tag_id}) = CInt({tag_id})
                """
                
                cursor.execute(tag_totals_query)
                tag_totals_row = cursor.fetchone()
                
                if tag_totals_row:
                    total_quantity += tag_totals_row[0] if tag_totals_row[0] is not None else 0
                    total_price += tag_totals_row[1] if tag_totals_row[1] is not None else 0
            
            discrepancy_query = f"""
            SELECT 
                Sum(
                    Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.counted_qty}))
                ) AS discrepancy_dollars,
                Count(*) AS discrepancy_tags
            FROM {queue.table}, {info.table}, {details_edit.table}
            WHERE {queue.table}.{queue.zone_queue_id} = {info.table}.{info.zone_queue_id}
                AND {info.table}.{info.tag} = {details_edit.table}.{details_edit.tag}
                AND {info.table}.{info.upc} = {details_edit.table}.{details_edit.sku}
                AND {info.table}.{info.counted_qty} = {details_edit.table}.{details_edit.qty}
                AND {info.table}.{info.zone_sku} = {details_edit.table}.{details_edit.zone_sku}
                AND {queue.table}.{queue.reason} = 'SERVICE_MISCOUNTED'
                AND {details_edit.table}.{details_edit.emp_no} = '{emp_no}'
            """
            
            cursor.execute(discrepancy_query)
            discrepancy_row = cursor.fetchone()
            
            discrepancy_dollars = discrepancy_row[0] if discrepancy_row[0] is not None else 0
            discrepancy_tags = discrepancy_row[1] if discrepancy_row[1] is not None else 0
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