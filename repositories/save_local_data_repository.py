"""Database query functions for managing locally stored."""
import pyodbc

from models import InventoryTable, EmployeeTable, ZoneTable


def create_tables_if_not_exists(conn: pyodbc.Connection) -> None:
    """Creates tables if they do not exist.

    Args:
        conn: Database connection object
    """
    cursor = conn.cursor()
    inventory = InventoryTable()
    emp = EmployeeTable()
    zone = ZoneTable()
    existing_tables = [row.table_name for row in cursor.tables(tableType='TABLE')]

    create_tables_queries = {
        inventory.table: f"""
            CREATE TABLE {inventory.table} (
                {inventory.store_number} TEXT(50) PRIMARY KEY,
                {inventory.store_name} TEXT(50),
                {inventory.job_datetime} TEXT(50),
                {inventory.store_address} TEXT(255)
            )
        """,
        emp.table: f"""
            CREATE TABLE {emp.table} (
                {emp.emp_number} TEXT(50) PRIMARY KEY,
                {emp.store_number} TEXT(50),
                {emp.emp_name} TEXT(255),
                {emp.total_tags} INTEGER,
                {emp.total_quantity} INTEGER,
                {emp.total_price} DOUBLE,
                {emp.discrepancy_dollars} DOUBLE,
                {emp.discrepancy_tags} INTEGER,
                {emp.hours} DOUBLE
            )
        """,
        zone.table: f"""
            CREATE TABLE {zone.table} (
                {zone.zone_id} TEXT(50) PRIMARY KEY,
                {zone.store_number} TEXT(50),
                {zone.zone_description} TEXT(255),
                {zone.total_tags} INTEGER,
                {zone.total_quantity} INTEGER,
                {zone.total_price} DOUBLE,
                {zone.discrepancy_dollars} DOUBLE,
                {zone.discrepancy_tags} INTEGER
            )
        """
    }

    for table_name, create_sql in create_tables_queries.items():
        if table_name not in existing_tables:
            cursor.execute(create_sql)
            conn.commit()

    cursor.close()


def check_inventory_exists(conn: pyodbc.Connection, store_data: dict) -> bool:
    """Checks if current inventory exists.

    Args:
        conn: pyodbc Connection object
        store_data: Dictionary containing store data
    """
    cursor = conn.cursor()
    inventory = InventoryTable()

    inventory_exists_query = f"SELECT TOP 1 1 FROM {inventory.table} WHERE {inventory.store_number} = ?"
    cursor.execute(inventory_exists_query, (store_data["store_number"],))
    exists = cursor.fetchone() is not None

    cursor.close()
    return exists


def insert_inventory_data(conn: pyodbc.Connection, store_data: dict) -> None:
    """Inserts inventory record for a given store.

    Args:
        conn: pyodbc Connection object
        store_data: Dictionary containing store data
    """
    cursor = conn.cursor()
    inventory = InventoryTable()

    inventory_query = f"""
        INSERT INTO {inventory.table} (
            {inventory.store_number}, {inventory.store_name}, {inventory.job_datetime}, {inventory.store_address}
        ) VALUES (?, ?, ?, ?)
    """

    cursor.execute(inventory_query, (store_data["store_number"], store_data["store"], store_data["inventory_datetime"], store_data["store_address"]))
    conn.commit()

    cursor.close()


def insert_employee_data(conn: pyodbc.Connection, store_data: dict, emp_data: dict) -> None:
    """Inserts employee record for a given store.

    Args:
        conn: pyodbc Connection object
        store_data: Dictionary containing store data
        emp_data: Dictionary containing emp data
    """
    cursor = conn.cursor()
    emp = EmployeeTable()

    emp_query = f"""
        INSERT INTO {emp.table} (
            {emp.store_number}, {emp.emp_number}, {emp.emp_name}, {emp.total_tags}, {emp.total_quantity}, {emp.total_price}, 
            {emp.discrepancy_dollars}, {emp.discrepancy_tags}, {emp.hours}
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        emp_query, (
            store_data["store_number"], emp_data["emp_number"], emp_data["emp_name"], emp_data["total_tags"], emp_data["total_quantity"], emp_data["total_price"],
            emp_data["discrepancy_dollars"], emp_data["discrepancy_tags"], emp_data["hours"]
        )
   )
    conn.commit()

    cursor.close()


def insert_zone_data(conn: pyodbc.Connection, store_data: dict, zone_data: dict) -> None:
    """Inserts zone record for a given store.

    Args:
        conn: pyodbc Connection object
        store_data: Dictionary containing store data
        zone_data: Dictionary containing zone data
    """
    cursor = conn.cursor()
    zone = ZoneTable()

    zone_query = f"""
        INSERT INTO {zone.table} (
            {zone.store_number}, {zone.zone_id}, {zone.zone_description}, {zone.total_tags}, {zone.total_quantity}, {zone.total_price}, 
            {zone.discrepancy_dollars}, {zone.discrepancy_tags}
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        zone_query, (
            store_data["store_number"], zone_data["zone_id"], zone_data["zone_description"], zone_data["total_tags"], zone_data["total_quantity"],
            zone_data["total_price"], zone_data["discrepancy_dollars"], zone_data["discrepancy_tags"]
        )
    )
    conn.commit()

    cursor.close()


def update_employee_data(conn: pyodbc.Connection, store_data: dict, emp_data: dict) -> dict | None:
    """Updates employee record for a given store and returns the previous row.

    Args:
        conn: pyodbc Connection object
        store_data: Dictionary containing store data
        emp_data: Dictionary containing employee data

    Returns:
        Dictionary of the existing employee row before the update, or None if not found.
    """
    cursor = conn.cursor()
    emp = EmployeeTable()

    emp_query = f"""SELECT * FROM {emp.table} WHERE {emp.store_number} = ? AND {emp.emp_number} = ?"""
    cursor.execute(emp_query, (store_data["store_number"], emp_data["emp_number"]))
    existing_row = cursor.fetchone()

    if not existing_row:
        insert_employee_data(conn=conn, store_data=store_data, emp_data=emp_data)
        return None

    columns = [column[0] for column in cursor.description]
    prev_emp_data = dict(zip(columns, existing_row))

    emp_query = f"""
        UPDATE {emp.table}
        SET
            {emp.total_tags} = ?, {emp.total_quantity} = ?, {emp.total_price} = ?, {emp.discrepancy_dollars} = ?, 
            {emp.discrepancy_tags} = ?, {emp.hours} = ?
        WHERE {emp.store_number} = ? AND {emp.emp_number} = ?
    """

    cursor.execute(
        emp_query, (
            emp_data["total_tags"], emp_data["total_quantity"], emp_data["total_price"], emp_data["discrepancy_dollars"],
            emp_data["discrepancy_tags"], emp_data["hours"], store_data["store_number"], emp_data["emp_number"]
        )
    )
    conn.commit()

    cursor.close()
    return prev_emp_data


def update_zone_data(conn: pyodbc.Connection, store_data: dict, zone_data: dict) -> dict | None:
    """Updates zone record for a given store.

    Args:
        conn: pyodbc Connection object
        store_data: Dictionary containing store data
        zone_data: Dictionary containing zone data

    Returns:
        Dictionary of the existing zone row before the update, or None if not found.
    """
    cursor = conn.cursor()
    zone = ZoneTable()

    zone_query = f"""SELECT * FROM {zone.table} WHERE {zone.store_number} = ? AND {zone.zone_id} = ?"""
    cursor.execute(zone_query, (store_data["store_number"], zone_data["zone_id"]))
    existing_row = cursor.fetchone()

    if not existing_row:
        insert_zone_data(conn=conn, store_data=store_data, zone_data=zone_data)
        return None

    columns = [column[0] for column in cursor.description]
    prev_zone_data = dict(zip(columns, existing_row))

    zone_query = f"""
        UPDATE {zone.table}
        SET {zone.total_tags} = ?, {zone.total_quantity} = ?, {zone.total_price} = ?, {zone.discrepancy_dollars} = ?, {zone.discrepancy_tags} = ?
        WHERE {zone.store_number} = ? AND {zone.zone_id} = ?
    """

    cursor.execute(
        zone_query, (
            zone_data["total_tags"], zone_data["total_quantity"], zone_data["total_price"], zone_data["discrepancy_dollars"],
            zone_data["discrepancy_tags"], store_data["store_number"], zone_data["zone_id"]
        )
    )
    conn.commit()

    cursor.close()
    return prev_zone_data