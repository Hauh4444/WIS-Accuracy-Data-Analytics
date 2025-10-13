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
        
    Raises:
        ValueError: If connection is invalid or database schema is malformed
        RuntimeError: If critical employee data is missing or corrupted
    """
    emp_data = []

    try:
        if conn is None:
            raise ValueError("Database connection cannot be None")
        if not hasattr(conn, 'cursor'):
            raise ValueError("Invalid database connection object - missing cursor method")

        cursor = conn.cursor()
        term = TerminalControlTable()
        emp = EmpNamesTable()
        details = DetailsTable()
        queue = ZoneChangeQueueTable()
        info = ZoneChangeInfoTable()
        tag = TagTable()

        emp_tags_query = f"""
            SELECT DISTINCT 
                {details.table}.{details.emp_number},
                {details.table}.{details.tag_number}
            FROM {details.table}
        """
        cursor.execute(emp_tags_query)
        emp_tags_rows = cursor.fetchall()

        emp_tags_map = {}

        for emp_tags_row in emp_tags_rows:
            if emp_tags_row is None or len(emp_tags_row) != 2:
                raise RuntimeError(f"Invalid emp_tags query result structure - expected 2 columns, got {len(emp_tags_row) if emp_tags_row else 0}")

            emp_number = emp_tags_row[0] if emp_tags_row and emp_tags_row[0] else ""
            emp_tag = emp_tags_row[1] if emp_tags_row and emp_tags_row[1] else ""
            emp_tags_map.setdefault(emp_number, []).append(emp_tag)

        emp_query = f"""
            SELECT DISTINCT
                {emp.table}.{emp.emp_number},
                {emp.table}.{emp.emp_name}
            FROM {emp.table}
            INNER JOIN {term.table} ON {term.table}.{term.emp_number} = {emp.table}.{emp.emp_number}
        """
        cursor.execute(emp_query)
        emp_rows = cursor.fetchall()

        for emp_row in emp_rows:
            if emp_row is None or len(emp_row) != 2:
                raise RuntimeError(f"Invalid emp query result structure - expected 2 columns, got {len(emp_row) if emp_row else 0}")

            emp_number = emp_row[0] if emp_row and emp_row[0] else ""
            emp_name = emp_row[1] if emp_row and emp_row[1] else ""

            employee_tags = emp_tags_map.get(emp_number, [])
            if not employee_tags: continue
            placeholders = ",".join("?" for _ in employee_tags)

            emp_totals_query = f"""
                SELECT 
                    Sum({tag.table}.{tag.total_qty}),
                    Sum({tag.table}.{tag.total_price})
                FROM {tag.table}
                WHERE CInt({tag.table}.{tag.tag_number}) IN ({placeholders})
            """
            cursor.execute(emp_totals_query, employee_tags)
            emp_totals_row = cursor.fetchone()
            if emp_totals_row is None or len(emp_totals_row) != 2:
                raise RuntimeError(f"Invalid emp_totals query result - expected 2 columns, got {len(emp_totals_row) if emp_totals_row else 0}")

            total_quantity = emp_totals_row[0] if emp_totals_row[0] is not None else 0
            total_price = emp_totals_row[1] if emp_totals_row[1] is not None else 0
            tag_count = len(employee_tags)

            emp_discrepancies_query = f"""
                SELECT
                    {queue.table}.{queue.zone_id},
                    {queue.table}.{queue.tag_number},
                    {queue.table}.{queue.upc},
                    {queue.table}.{queue.price},
                    {info.table}.{info.quantity},
                    {queue.table}.{queue.quantity},
                    Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.quantity}))
                FROM {queue.table}
                INNER JOIN {info.table} ON {queue.table}.{queue.zone_queue_id} = {info.table}.{info.zone_queue_id}
                WHERE {queue.table}.{queue.reason} = 'SERVICE_MISCOUNTED'
                    AND CInt({queue.table}.{queue.tag_number}) IN ({placeholders})
                    AND Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.quantity})) > 50
                ORDER BY {queue.table}.{queue.tag_number}
            """
            cursor.execute(emp_discrepancies_query, employee_tags)
            emp_discrepancies_rows = cursor.fetchall()

            discrepancies = []
            discrepancy_dollars = 0
            discrepancy_tags_set = set()

            for emp_discrepancies_row in emp_discrepancies_rows:
                if len(emp_discrepancies_row) != 7:
                    raise RuntimeError(f"Invalid emp_discrepancies query result structure - expected 7 columns, got {len(emp_discrepancies_row) if emp_discrepancies_row else 0}")

                zone_id = emp_discrepancies_row[0] if emp_discrepancies_row and emp_discrepancies_row[0] is not None else 0
                tag_number = emp_discrepancies_row[1] if emp_discrepancies_row and emp_discrepancies_row[1] is not None else 0
                upc = emp_discrepancies_row[2] if emp_discrepancies_row and emp_discrepancies_row[2] is not None else 0
                price = emp_discrepancies_row[3] if emp_discrepancies_row and emp_discrepancies_row[3] is not None else 0
                counted_quantity = emp_discrepancies_row[4] if emp_discrepancies_row and emp_discrepancies_row[4] is not None else 0
                new_quantity = emp_discrepancies_row[5] if emp_discrepancies_row and emp_discrepancies_row[5] is not None else 0
                discrepancy_change = emp_discrepancies_row[6] if emp_discrepancies_row and emp_discrepancies_row[6] is not None else 0

                discrepancy_dollars += price
                discrepancy_tags_set.add(tag_number)
                discrepancies.append({
                    "zone_id": zone_id,
                    "tag_number": tag_number,
                    "upc": upc,
                    "price": price,
                    "counted_quantity": counted_quantity,
                    "new_quantity": new_quantity,
                    "discrepancy_dollars": discrepancy_change,
                })

            discrepancy_tags = len(discrepancy_tags_set)
            discrepancy_percent = (discrepancy_dollars / total_price * 100) if total_price > 0 else 0

            emp_data.append({
                'employee_number': emp_number,
                'employee_name': emp_name,
                'total_tags': tag_count,
                'total_quantity': total_quantity,
                'total_price': total_price,
                'total_discrepancy_dollars': discrepancy_dollars,
                'total_discrepancy_tags': discrepancy_tags,
                'discrepancy_percent': discrepancy_percent,
                'discrepancies': discrepancies
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

    return emp_data