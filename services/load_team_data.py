import pyodbc
from PyQt6 import QtWidgets

from services.models import DiscrepancyTable, TagTable


def load_team_data(conn: pyodbc.Connection) -> list[dict]:
    d, t = DiscrepancyTable(), TagTable()

    query = f"""
        SELECT  
            {d.table}.{d.department_number} AS department_number,
            {d.table}.{d.department_name} AS department_name
            COALESCE(SUM(ABS({d.table}.{d.dollar_change})), 0) AS total_discrepancy_dollars,
            COUNT(DISTINCT CASE 
                WHEN {d.table}.{d.dollar_change} IS NOT NULL 
                     AND {d.table}.{d.dollar_change} <> 0 
                THEN {t.table}.{t.tag_number} END
            ) AS total_discrepancy_tags,
            CASE 
                WHEN SUM({t.table}.{t.dollars}) = 0 THEN 0
                ELSE (COALESCE(SUM(ABS({d.table}.{d.dollar_change})), 0) * 100.0) / SUM({t.table}.{t.dollars})
            END AS discrepancy_percent,
            COUNT(DISTINCT {t.table}.{t.tag_number}) AS total_tags,
            SUM({t.table}.{t.qty}) AS total_quantity
        FROM {d.table}
        INNER JOIN {t.table}
            ON {d.table}.{d.tag_number} = {t.table}.{t.tag_number}
        GROUP BY {d.table}.{d.department_number}
        ORDER BY {d.table}.{d.department_number}
    """

    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
    except Exception as ex:
        QtWidgets.QMessageBox.critical(None, "Database Error", f"Failed to load team data:\n{ex}")
        return []

    if not rows:
        QtWidgets.QMessageBox.warning(None, "No Data", "No team records were found.")
        return []

    team_data = [
        {
            "department_number": row.department_number,
            "department_name": row.department_name,
            "total_discrepancy_dollars": row.total_discrepancy_dollars,
            "total_discrepancy_tags": row.total_discrepancy_tags,
            "discrepancy_percent": row.discrepancy_percent,
            "total_tags": row.total_tags,
            "total_quantity": row.total_quantity,
        }
        for row in rows
    ]

    return team_data