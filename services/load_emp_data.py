"""Employee data loader with inventory accuracy metrics."""
import pyodbc
from PyQt6 import QtWidgets

from services.models import TerminalControlTable, EmpNamesTable, DetailsTable, ZoneChangeQueueTable, ZoneChangeInfoTable, TagTable


def load_emp_data(conn: pyodbc.Connection) -> list[dict]:
    """Load employee data with discrepancy calculations.
    
    Business rule: Only discrepancies >$50 with reason='SERVICE_MISCOUNTED' are counted against the team.

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

        emp_tags_query = f"""
            SELECT DISTINCT 
                {details.table}.{details.emp_no},
                {details.table}.{details.tag}
            FROM {details.table}
        """
        cursor.execute(emp_tags_query)
        emp_tags_rows = cursor.fetchall()
        emp_tags_map = {}
        for emp_tags_row in emp_tags_rows: # Build employee-to-tags mapping once to avoid N+1 queries in the main loop
            emp_tags_map.setdefault(emp_tags_row[0], []).append(emp_tags_row[1])

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

            employee_tags = emp_tags_map.get(emp_no, [])
            if not employee_tags: continue
            tags_filter = ','.join(employee_tags)
            tag_count = len(employee_tags)

            emp_totals_query = f"""
                SELECT 
                    Sum({tag.table}.{tag.total_qty}),
                    Sum({tag.table}.{tag.total_ext})
                FROM {tag.table}
                WHERE CInt({tag.table}.{tag.tag_no}) IN ({tags_filter})
            """
            cursor.execute(emp_totals_query)
            emp_totals_row = cursor.fetchone()
            total_quantity = emp_totals_row[0] or 0
            total_price = emp_totals_row[1] or 0

            emp_discrepancy_query = f"""
                SELECT 
                    Sum(Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.counted_qty}))),
                    (
                        SELECT Count(*)
                        FROM (
                            SELECT DISTINCT {queue.table}.{queue.tag}
                            FROM {queue.table}
                            INNER JOIN {info.table} ON {queue.table}.{queue.zone_queue_id} = {info.table}.{info.zone_queue_id}
                            WHERE {queue.table}.{queue.reason} = 'SERVICE_MISCOUNTED'
                                AND CInt({queue.table}.{queue.tag}) IN ({tags_filter})
                                AND Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.counted_qty})) > 50
                        )
                    )
                FROM {queue.table}
                INNER JOIN {info.table} ON {queue.table}.{queue.zone_queue_id} = {info.table}.{info.zone_queue_id}
                WHERE {queue.table}.{queue.reason} = 'SERVICE_MISCOUNTED'
                    AND CInt({queue.table}.{queue.tag}) IN ({tags_filter})
                    AND Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.counted_qty})) > 50
            """
            cursor.execute(emp_discrepancy_query)
            emp_discrepancy_row = cursor.fetchone()
            discrepancy_dollars = emp_discrepancy_row[0] if emp_discrepancy_row and emp_discrepancy_row[0] is not None else 0
            discrepancy_tags = emp_discrepancy_row[1] if emp_discrepancy_row and emp_discrepancy_row[1] is not None else 0
            discrepancy_percent = (discrepancy_dollars / total_price * 100) if total_price > 0 else 0

            discrepancies_query = f"""
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
            cursor.execute(discrepancies_query)
            discrepancies_rows = cursor.fetchall()
            discrepancies = []
            for discrepancies_row in discrepancies_rows:
                discrepancies.append({
                    "zone_id": discrepancies_row[0] if discrepancies_row and discrepancies_row[0] is not None else 0,
                    "tag": discrepancies_row[1] if discrepancies_row and discrepancies_row[1] is not None else 0,
                    "upc": discrepancies_row[2] if discrepancies_row and discrepancies_row[2] is not None else 0,
                    "price": discrepancies_row[3] if discrepancies_row and discrepancies_row[3] is not None else 0,
                    "counted_qty": discrepancies_row[4] if discrepancies_row and discrepancies_row[4] is not None else 0,
                    "new_quantity": discrepancies_row[5] if discrepancies_row and discrepancies_row[5] is not None else 0,
                    "discrepancy_dollars": discrepancies_row[6] if discrepancies_row and discrepancies_row[6] is not None else 0,
                })

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
    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Database Error", f"Failed to load employee data: {str(e)}")

    return emp_data