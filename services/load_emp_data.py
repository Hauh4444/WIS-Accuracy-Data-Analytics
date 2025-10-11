import pyodbc
from PyQt6 import QtWidgets

from services.models import TerminalControlTable, EmpNamesTable, DetailsTable, ZoneChangeQueueTable, ZoneChangeInfoTable, TagTable


def load_emp_data(conn: pyodbc.Connection) -> list[dict]:
    """Load employee data with discrepancy calculations from the database.

    Args:
        conn: Database connection object

    Returns:
        List of dictionaries containing employee data with totals and discrepancies
    """
    emp_data = []

    try:
        cursor = conn.cursor()
        term = TerminalControlTable()
        emp = EmpNamesTable()
        details = DetailsTable()
        queue = ZoneChangeQueueTable()
        info = ZoneChangeInfoTable()
        tag = TagTable()

        emp_query = f"""
            SELECT DISTINCT
                {emp.table}.{emp.emp_no},
                {emp.table}.{emp.emp_name}
            FROM {emp.table}
            INNER JOIN {term.table} ON {term.table}.{term.emp_no} = {emp.table}.{emp.emp_no}
        """
        cursor.execute(emp_query)
        emp_rows = cursor.fetchall()

        for emp_row in emp_rows:
            emp_no = emp_row[0]
            emp_name = emp_row[1]

            tags_query = f"""
                SELECT DISTINCT {details.table}.{details.tag}
                FROM {details.table}
                WHERE {details.table}.{details.emp_no} = '{emp_no}'
            """
            cursor.execute(tags_query)
            tag_rows = cursor.fetchall()
            tag_count = len(tag_rows)

            employee_tags = [str(tag_row[0]) for tag_row in tag_rows]
            if not employee_tags:
                emp_data.append({
                    'employee_id': emp_no,
                    'employee_name': emp_name,
                    'total_tags': 0,
                    'total_quantity': 0,
                    'total_price': 0,
                    'total_discrepancy_dollars': 0,
                    'total_discrepancy_tags': 0,
                    'discrepancy_percent': 0,
                    'discrepancies': []
                })
                continue

            tags_filter = ','.join(employee_tags)

            tag_totals_query = f"""
                SELECT 
                    Sum(IIf(IsNull({tag.table}.{tag.total_qty}),0,{tag.table}.{tag.total_qty})) AS total_qty_sum,
                    Sum(IIf(IsNull({tag.table}.{tag.total_ext}),0,{tag.table}.{tag.total_ext})) AS total_ext_sum
                FROM {tag.table}
                WHERE CInt({tag.table}.{tag.tag_no}) IN ({tags_filter})
            """
            cursor.execute(tag_totals_query)
            totals_row = cursor.fetchone()
            total_quantity = totals_row[0] or 0
            total_price = totals_row[1] or 0

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
            cursor.execute(discrepancy_dollars_query)
            discrepancy_dollars_row = cursor.fetchone()
            discrepancy_dollars = discrepancy_dollars_row[0] if discrepancy_dollars_row and discrepancy_dollars_row[0] is not None else 0

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
            cursor.execute(discrepancy_tags_query)
            discrepancy_tags_row = cursor.fetchone()
            discrepancy_tags = discrepancy_tags_row[0] if discrepancy_tags_row and discrepancy_tags_row[0] is not None else 0
            discrepancy_percent = (discrepancy_dollars / total_price * 100) if total_price > 0 else 0

            discrepancy_query = f"""
                SELECT
                    {queue.table}.{queue.zone_id},
                    {queue.table}.{queue.tag},
                    {queue.table}.{queue.upc},
                    {queue.table}.{queue.price},
                    {info.table}.{info.counted_qty},
                    {queue.table}.{queue.quantity},
                    Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.counted_qty}))
                FROM {queue.table}
                INNER JOIN {info.table} ON {queue.table}.{queue.zone_queue_id} = {info.table}.{info.zone_queue_id}
                WHERE {queue.table}.{queue.reason} = 'SERVICE_MISCOUNTED'
                    AND CInt({queue.table}.{queue.tag}) IN ({tags_filter})
                    AND Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.counted_qty})) > 50
                ORDER BY {queue.table}.{queue.tag}
            """
            cursor.execute(discrepancy_query)
            discrepancy_rows = cursor.fetchall()
            discrepancies = [
                {
                    "zone_id": row[0],
                    "tag": row[1],
                    "upc": row[2],
                    "price": row[3],
                    "counted_qty": row[4],
                    "new_quantity": row[5],
                    "discrepancy_dollars": row[6],
                }
                for row in discrepancy_rows
            ]

            emp_data.append({
                'employee_id': emp_no,
                'employee_name': emp_name,
                'total_tags': tag_count,
                'total_quantity': total_quantity,
                'total_price': total_price,
                'total_discrepancy_dollars': discrepancy_dollars,
                'total_discrepancy_tags': discrepancy_tags,
                'discrepancy_percent': discrepancy_percent,
                'discrepancies': discrepancies
            })

        return emp_data
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Database Error", f"Failed to load employee data: {str(e)}")

    return emp_data