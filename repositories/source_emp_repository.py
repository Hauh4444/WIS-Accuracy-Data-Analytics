"""Database query functions for retrieving employee data."""
import pyodbc

from models.source_models import TerminalControlTable, EmpNamesTable, DetailsTable, DLoadErrorsTable, ZoneChangeQueueTable, ZoneChangeInfoTable, TagTable


def fetch_emp_tags_data(conn: pyodbc.Connection) -> list[pyodbc.Row] | None:
    """Fetch employee tags data from the database.

    Args:
        conn: Database connection object

    Returns:
        List of pyodbc rows containing employee tags data
    """
    cursor = conn.cursor()
    details = DetailsTable()

    emp_tags_query = f"""
        SELECT DISTINCT 
            {details.table}.{details.emp_number},
            {details.table}.{details.tag_number}
        FROM {details.table}
    """
    cursor.execute(emp_tags_query)
    emp_tags_rows = cursor.fetchall()

    cursor.close()
    return emp_tags_rows


def fetch_duplicate_tags_data(conn: pyodbc.Connection) -> list[pyodbc.Row] | None:
    """Fetch duplicate tags data from the database.

    Args:
        conn: Database connection object

    Returns:
        List of pyodbc rows containing duplicate tags data
    """
    cursor = conn.cursor()
    dload = DLoadErrorsTable()

    duplicate_tags_query = f"""
        SELECT DISTINCT
            {dload.table}.{dload.tag_number}
        FROM {dload.table}
        WHERE {dload.table}.{dload.error_msg} = 'Duplicate Tag'
    """
    cursor.execute(duplicate_tags_query)
    duplicate_tags_rows = cursor.fetchall()

    cursor.close()
    return duplicate_tags_rows


def fetch_emp_data(conn: pyodbc.Connection) -> list[pyodbc.Row] | None:
    """Fetch employee data from the database.

    Args:
        conn: Database connection object

    Returns:
        List of pyodbc rows containing employee data
    """
    cursor = conn.cursor()
    emp = EmpNamesTable()
    term = TerminalControlTable()

    emp_query = f"""
        SELECT DISTINCT
            {emp.table}.{emp.emp_number},
            {emp.table}.{emp.emp_name}
        FROM {emp.table}
        INNER JOIN {term.table} ON {term.table}.{term.emp_number} = {emp.table}.{emp.emp_number}
    """
    cursor.execute(emp_query)
    emp_rows = cursor.fetchall()

    cursor.close()
    return emp_rows


def fetch_emp_totals_data(conn: pyodbc.Connection, tags_filter: str) -> pyodbc.Row | None:
    """Fetch employee totals data from the database.

    Args:
        conn: Database connection object
        tags_filter: Comma-separated string of tag numbers to include in the aggregation query.

    Returns:
        Pyodbc row containing employee totals data
    """
    cursor = conn.cursor()
    tag = TagTable()

    # Can't parameterize tags since Access will throw a 'System resources exceeded' error
    emp_totals_query = f"""
        SELECT 
            Sum({tag.table}.{tag.total_quantity}),
            Sum({tag.table}.{tag.total_price})
        FROM {tag.table}
        WHERE CInt({tag.table}.{tag.tag_number}) IN ({tags_filter})
    """
    cursor.execute(emp_totals_query)
    emp_totals_row = cursor.fetchone()

    cursor.close()
    return emp_totals_row


def fetch_emp_line_totals_data(conn: pyodbc.Connection, tags_filter: str, emp_number: str) -> pyodbc.Row | None:
    """Fetch employee totals data by line from the database.

    Args:
        conn: Database connection object
        tags_filter: Comma-separated string of tag numbers to include in the aggregation query.
        emp_number: The employee number to match

    Returns:
        Pyodbc row containing employee totals data
    """
    cursor = conn.cursor()
    details = DetailsTable()

    # Can't parameterize tags since Access will throw a 'System resources exceeded' error
    emp_totals_query = f"""
        SELECT 
            Sum({details.table}.{details.quantity}),
            Sum({details.table}.{details.price})
        FROM {details.table}
        WHERE CInt({details.table}.{details.tag_number}) IN ({tags_filter})
            AND {details.table}.{details.emp_number} = ?
    """
    cursor.execute(emp_totals_query, (emp_number,))
    emp_totals_row = cursor.fetchone()

    cursor.close()
    return emp_totals_row


def fetch_emp_discrepancies_data(conn: pyodbc.Connection, tags_filter: str) -> list[pyodbc.Row] | None:
    """Fetch employee discrepancy data from the database.

    Args:
        conn: Database connection object
        tags_filter: Comma-separated string of tag numbers to include in the aggregation query.

    Returns:
        List of pyodbc rows containing employee discrepancy data
    """
    cursor = conn.cursor()
    queue = ZoneChangeQueueTable()
    info = ZoneChangeInfoTable()

    # Can't parameterize tags since Access will throw a 'System resources exceeded' error
    emp_discrepancies_query = f"""
        SELECT
            {queue.table}.{queue.zone_id},
            {queue.table}.{queue.tag_number},
            {queue.table}.{queue.upc},
            {info.table}.{info.quantity},
            {queue.table}.{queue.quantity},
            {queue.table}.{queue.price},
            Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.quantity}))
        FROM {queue.table}
        INNER JOIN {info.table} ON {queue.table}.{queue.zone_queue_id} = {info.table}.{info.zone_queue_id}
        WHERE {queue.table}.{queue.reason} = 'SERVICE_MISCOUNTED'
            AND CInt({queue.table}.{queue.tag_number}) IN ({tags_filter})
            AND Abs(({queue.table}.{queue.price} * {queue.table}.{queue.quantity}) - ({queue.table}.{queue.price} * {info.table}.{info.quantity})) > 50
        ORDER BY {queue.table}.{queue.tag_number}
    """
    cursor.execute(emp_discrepancies_query)
    emp_discrepancies_rows = cursor.fetchall()

    cursor.close()
    return emp_discrepancies_rows


def fetch_line_data(conn: pyodbc.Connection, tag_number: str, upc: str) -> pyodbc.Row | None:
    """Fetch line data from the database.

    Args:
        conn: Database connection object
        tag_number: The employee tag number to match.
        upc: The product UPC to match.

    Returns:
        Pyodbc row containing line data
    """
    cursor = conn.cursor()
    details = DetailsTable()

    verify_line_query = f"""
        SELECT {details.table}.{details.emp_number}
        FROM {details.table}
        WHERE {details.table}.{details.tag_number} = ?
            AND {details.table}.{details.upc} = ?
    """
    cursor.execute(verify_line_query, (tag_number, upc))
    verify_line_row = cursor.fetchone()

    cursor.close()
    return verify_line_row