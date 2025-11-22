"""Database query functions for managing locally stored."""
import pyodbc

from models.local_models import InventoryTable, EmployeeTable, EmployeeTotalsTable, ZoneTable, ZoneTotalsTable


def create_tables_if_not_exists(conn: pyodbc.Connection) -> None:
    """Creates tables if they do not exist.

    Args:
        conn: Database connection object
    """
    cursor = conn.cursor()
    inventory = InventoryTable()
    emp = EmployeeTable()
    emp_totals = EmployeeTotalsTable()
    zone = ZoneTable()
    zone_totals = ZoneTotalsTable()
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
        emp_totals.table: f"""
            CREATE TABLE {emp_totals.table} (
                {emp_totals.emp_number} TEXT(50) PRIMARY KEY,
                {emp_totals.emp_name} TEXT(255),
                {emp_totals.total_tags} INTEGER,
                {emp_totals.total_quantity} INTEGER,
                {emp_totals.total_price} DOUBLE,
                {emp_totals.discrepancy_dollars} DOUBLE,
                {emp_totals.discrepancy_tags} INTEGER,
                {emp_totals.stores} INTEGER,
                {emp_totals.hours} DOUBLE
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
        zone_totals.table: f"""
            CREATE TABLE {zone_totals.table} (
                {zone_totals.zone_id} TEXT(50) PRIMARY KEY,
                {zone_totals.zone_description} TEXT(255),
                {zone_totals.total_tags} INTEGER,
                {zone_totals.total_quantity} INTEGER,
                {zone_totals.total_price} DOUBLE,
                {zone_totals.discrepancy_dollars} DOUBLE,
                {zone_totals.discrepancy_tags} INTEGER,
                {zone_totals.stores} INTEGER
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


def check_employee_totals_exist(conn: pyodbc.Connection, emp_data: dict) -> bool:
    """Checks if employee record exists for employee totals

    Args:
        conn: pyodbc Connection object
        emp_data: Dictionary containing emp data
    """
    cursor = conn.cursor()
    emp_totals = EmployeeTotalsTable()

    employee_totals_exist_query = f"SELECT TOP 1 1 FROM {emp_totals.table} WHERE {emp_totals.emp_number} = ?"
    cursor.execute(employee_totals_exist_query, (emp_data["emp_number"],))
    exists = cursor.fetchone() is not None

    cursor.close()
    return exists


def check_zone_totals_exist(conn: pyodbc.Connection, zone_data: dict) -> bool:
    """Checks if zone record exists for zone totals

    Args:
        conn: pyodbc Connection object
        zone_data: Dictionary containing zone data
    """
    cursor = conn.cursor()
    zone_totals = ZoneTotalsTable()

    zone_totals_exist_query = f"SELECT TOP 1 1 FROM {zone_totals.table} WHERE {zone_totals.zone_id} = ?"
    cursor.execute(zone_totals_exist_query, (zone_data["zone_id"],))
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


def insert_employee_totals_data(conn: pyodbc.Connection, emp_data: dict) -> None:
    """Inserts employee totals record.

    Args:
        conn: pyodbc Connection object
        emp_data: Dictionary containing emp data
    """
    cursor = conn.cursor()
    emp_totals = EmployeeTotalsTable()
    
    emp_totals_query = f"""
        INSERT INTO {emp_totals.table} (
            {emp_totals.emp_number}, {emp_totals.emp_name}, {emp_totals.total_tags}, {emp_totals.total_quantity}, {emp_totals.total_price},
            {emp_totals.discrepancy_dollars}, {emp_totals.discrepancy_tags}, {emp_totals.hours}, {emp_totals.stores}
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        emp_totals_query, (
            emp_data["emp_number"], emp_data["emp_name"], emp_data["total_tags"], emp_data["total_quantity"], emp_data["total_price"],
            emp_data["discrepancy_dollars"], emp_data["discrepancy_tags"], emp_data["hours"], 1
        )
    )
    conn.commit()

    cursor.close()


def insert_zone_totals_data(conn: pyodbc.Connection, zone_data: dict) -> None:
    """Inserts zone totals record.

    Args:
        conn: pyodbc Connection objectstore
        zone_data: Dictionary containing zone data
    """
    cursor = conn.cursor()
    zone_totals = ZoneTotalsTable()

    zone_totals_query = f"""
        INSERT INTO {zone_totals.table} (
            {zone_totals.zone_id}, {zone_totals.zone_description}, {zone_totals.total_tags}, {zone_totals.total_quantity}, {zone_totals.total_price},
            {zone_totals.discrepancy_dollars}, {zone_totals.discrepancy_tags}, {zone_totals.stores}
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(
        zone_totals_query, (
            zone_data["zone_id"], zone_data["zone_description"], zone_data["total_tags"], zone_data["total_quantity"], zone_data["total_price"],
            zone_data["discrepancy_dollars"], zone_data["discrepancy_tags"], 1
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


def update_employee_totals_data(conn: pyodbc.Connection, prev_emp_data: dict | None, emp_data: dict) -> None:
    """Updates employee totals record.

    Args:
        conn: pyodbc Connection object
        prev_emp_data: Dictionary of the existing employee row before the update, or None if not found
        emp_data: Dictionary containing emp data
    """
    cursor = conn.cursor()
    emp = EmployeeTable()
    emp_totals = EmployeeTotalsTable()

    total_tags = emp_data["total_tags"] - prev_emp_data.get(emp.total_tags, 0) if prev_emp_data else emp_data["total_tags"]
    total_qty = emp_data["total_quantity"] - prev_emp_data.get(emp.total_quantity, 0) if prev_emp_data else emp_data["total_quantity"]
    total_price = emp_data["total_price"] - prev_emp_data.get(emp.total_price, 0) if prev_emp_data else emp_data["total_price"]
    discrepancy_dollars = emp_data["discrepancy_dollars"] - prev_emp_data.get(emp.discrepancy_dollars, 0) if prev_emp_data else emp_data["discrepancy_dollars"]
    discrepancy_tags = emp_data["discrepancy_tags"] - prev_emp_data.get(emp.discrepancy_tags, 0) if prev_emp_data else emp_data["discrepancy_tags"]
    hours = emp_data["hours"] - prev_emp_data.get(emp.hours, 0) if prev_emp_data else emp_data["hours"]
    store_increment = 0 if prev_emp_data else 1

    emp_totals_query = f"""
        UPDATE {emp_totals.table}
        SET
            {emp_totals.total_tags} = {emp_totals.total_tags} + ?, {emp_totals.total_quantity} = {emp_totals.total_quantity} + ?,
            {emp_totals.total_price} = {emp_totals.total_price} + ?, {emp_totals.discrepancy_dollars} = {emp_totals.discrepancy_dollars} + ?,
            {emp_totals.discrepancy_tags} = {emp_totals.discrepancy_tags} + ?, {emp_totals.hours} = {emp_totals.hours} + ?,
            {emp_totals.stores} = {emp_totals.stores} + ?
        WHERE {emp_totals.emp_number} = ?
    """

    cursor.execute(emp_totals_query, (
        total_tags, total_qty, total_price, discrepancy_dollars, discrepancy_tags, hours, store_increment, emp_data["emp_number"]
    ))
    conn.commit()

    cursor.close()


def update_zone_totals_data(conn: pyodbc.Connection, prev_zone_data: dict | None, zone_data: dict) -> None:
    """Updates zone totals record.

    Args:
        conn: pyodbc Connection object
        prev_zone_data: Dictionary of the existing zone row before the update, or None if not found
        zone_data: Dictionary containing zone data
    """
    cursor = conn.cursor()
    zone = ZoneTable()
    zone_totals = ZoneTotalsTable()

    total_tags = zone_data["total_tags"] - prev_zone_data.get(zone.total_tags, 0) if prev_zone_data else zone_data["total_tags"]
    total_qty = zone_data["total_quantity"] - prev_zone_data.get(zone.total_quantity, 0) if prev_zone_data else zone_data["total_quantity"]
    total_price = zone_data["total_price"] - prev_zone_data.get(zone.total_price, 0) if prev_zone_data else zone_data["total_price"]
    discrepancy_dollars = zone_data["discrepancy_dollars"] - prev_zone_data.get(zone.discrepancy_dollars, 0) if prev_zone_data else zone_data["discrepancy_dollars"]
    discrepancy_tags = zone_data["discrepancy_tags"] - prev_zone_data.get(zone.discrepancy_tags,0) if prev_zone_data else zone_data["discrepancy_tags"]
    store_increment = 0 if prev_zone_data else 1

    zone_totals_query = f"""
        UPDATE {zone_totals.table}
        SET
            {zone_totals.total_tags} = {zone_totals.total_tags} + ?, {zone_totals.total_quantity} = {zone_totals.total_quantity} + ?,
            {zone_totals.total_price} = {zone_totals.total_price} + ?, {zone_totals.discrepancy_dollars} = {zone_totals.discrepancy_dollars} + ?,
            {zone_totals.discrepancy_tags} = {zone_totals.discrepancy_tags} + ?, {zone_totals.stores} = {zone_totals.stores} + ?
        WHERE {zone_totals.zone_id} = ?
    """
    cursor.execute(zone_totals_query, (
        total_tags, total_qty, total_price, discrepancy_dollars, discrepancy_tags, store_increment, zone_data["zone_id"]
    ))
    conn.commit()

    cursor.close()