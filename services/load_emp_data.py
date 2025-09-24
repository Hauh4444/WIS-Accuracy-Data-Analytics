import pyodbc
from PyQt6 import QtWidgets

from services.models import DiscrepancyTable, TagTable, EmployeeTable


def load_emp_data(conn: pyodbc.Connection) -> list[dict]:
    d, t, e = DiscrepancyTable(), TagTable(), EmployeeTable()

    query = f"""
        SELECT 
            {t.table}.{t.employee_id} AS employee_id,
            {e.table}.{e.employee_name} AS employee_name,
            COUNT(DISTINCT CASE 
                WHEN {d.table}.{d.dollar_change} IS NOT NULL 
                     AND {d.table}.{d.dollar_change} <> 0 
                THEN {t.table}.{t.tag_number} END
            ) AS total_discrepancy_tags,
            COALESCE(SUM(ABS({d.table}.{d.dollar_change})), 0) AS total_discrepancy_dollars,
            SUM({t.table}.{t.dollars}) AS total_dollars,
            CASE 
                WHEN SUM({t.table}.{t.dollars}) = 0 THEN 0
                ELSE (COALESCE(SUM(ABS({d.table}.{d.dollar_change})), 0) * 100.0) / SUM({t.table}.{t.dollars})
            END AS discrepancy_percent,
            COUNT(DISTINCT {t.table}.{t.tag_number}) AS total_tags,
            SUM({t.table}.{t.qty}) AS total_quantity
        FROM {t.table}
        LEFT JOIN {d.table}
            ON {d.table}.{d.tag_number} = {t.table}.{t.tag_number}
        LEFT JOIN {e.table}
            ON {e.table}.{e.employee_id} = {t.table}.{t.employee_id}
        GROUP BY 
            {t.table}.{t.employee_id},
            {e.table}.{e.employee_name}
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
    except Exception as ex:
        QtWidgets.QMessageBox.critical(None, "Database Error", f"Failed to load employee data:\n{ex}")
        return []

    if not rows:
        QtWidgets.QMessageBox.warning(None, "No Data", "No employee records were found.")
        return []

    emp_data = [
        {
            "employee_id": row.employee_id,
            "employee_name": row.employee_name,
            "total_discrepancy_tags": row.total_discrepancy_tags,
            "total_discrepancy_dollars": row.total_discrepancy_dollars,
            "discrepancy_percent": row.discrepancy_percent,
            "total_tags": row.total_tags,
            "total_quantity": row.total_quantity,
        }
        for row in rows
    ]

    return emp_data