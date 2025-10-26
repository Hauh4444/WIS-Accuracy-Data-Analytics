"""Employee data loader with inventory accuracy metrics."""
import pyodbc
from PyQt6 import QtWidgets

from repositories.emp_repository import fetch_emp_tags_data, fetch_duplicate_tags_data, fetch_emp_data, fetch_emp_totals_data, fetch_emp_discrepancies_data, fetch_line_data


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

        emp_tags_map = {}
        emp_tags_rows = fetch_emp_tags_data(conn=conn)
        for emp_tags_row in emp_tags_rows:
            if emp_tags_row is None or len(emp_tags_row) != 2:
                raise RuntimeError(f"Invalid emp_tags query result structure - expected 2 columns, got {len(emp_tags_row) if emp_tags_row else 0}")

            emp_number = emp_tags_row[0] if emp_tags_row and emp_tags_row[0] is not None else ""
            emp_tag = emp_tags_row[1] if emp_tags_row and emp_tags_row[1] is not None else ""
            emp_tags_map.setdefault(emp_number, []).append(emp_tag)

        duplicate_tags_map = {}
        duplicate_tags_rows = fetch_duplicate_tags_data(conn=conn)
        for duplicate_tags_row in duplicate_tags_rows:
            if duplicate_tags_row is None or len(duplicate_tags_row) != 2:
                raise RuntimeError(f"Invalid duplicate_tags query result structure - expected 2 columns, got {len(duplicate_tags_row) if duplicate_tags_row else 0}")
            
            emp_number = duplicate_tags_row[0] if duplicate_tags_row and duplicate_tags_row[0] is not None else ""
            emp_tag = duplicate_tags_row[1] if duplicate_tags_row and duplicate_tags_row[1] is not None else ""
            duplicate_tags_map.setdefault(emp_number, []).append(emp_tag)

        emp_rows = fetch_emp_data(conn=conn)
        for emp_row in emp_rows:
            if emp_row is None or len(emp_row) != 2:
                raise RuntimeError(f"Invalid emp query result structure - expected 2 columns, got {len(emp_row) if emp_row else 0}")

            emp_data_row = {
                "emp_number": emp_row[0] if emp_row and emp_row[0] else "",
                "emp_name": emp_row[1] if emp_row and emp_row[1] else "",
                "total_tags": 0,
                "total_quantity": 0,
                "total_price": 0.0,
                "discrepancies": [],
                "discrepancy_dollars": 0.0,
                "discrepancy_tags": 0,
                "discrepancy_percent": 0.0
            }

            emp_tags = emp_tags_map.get(emp_data_row["emp_number"], [])
            if not emp_tags: continue
            tags_filter = ",".join(emp_tags) # Can't parameterize tags since Access will throw a 'System resources exceeded' error

            emp_totals_row = fetch_emp_totals_data(conn=conn, tags_filter=tags_filter)
            if emp_totals_row is None or len(emp_totals_row) != 2:
                raise RuntimeError(f"Invalid emp_totals query result - expected 2 columns, got {len(emp_totals_row) if emp_totals_row else 0}")

            emp_data_row["total_tags"] = len(emp_tags)
            emp_data_row["total_quantity"] = emp_totals_row[0] if emp_totals_row[0] is not None else 0
            emp_data_row["total_price"] = emp_totals_row[1] if emp_totals_row[1] is not None else 0
            discrepancy_tags_set = set()

            emp_discrepancies_rows = fetch_emp_discrepancies_data(conn=conn, tags_filter=tags_filter)
            for emp_discrepancies_row in emp_discrepancies_rows:
                if len(emp_discrepancies_row) != 7:
                    raise RuntimeError(f"Invalid emp_discrepancies query result structure - expected 7 columns, got {len(emp_discrepancies_row) if emp_discrepancies_row else 0}")

                discrepancy_row = {
                    "zone_id": emp_discrepancies_row[0] if emp_discrepancies_row and emp_discrepancies_row[0] is not None else 0,
                    "tag_number": emp_discrepancies_row[1] if emp_discrepancies_row and emp_discrepancies_row[1] is not None else 0,
                    "upc": emp_discrepancies_row[2] if emp_discrepancies_row and emp_discrepancies_row[2] is not None else 0,
                    "price": emp_discrepancies_row[3] if emp_discrepancies_row and emp_discrepancies_row[3] is not None else 0,
                    "counted_quantity": emp_discrepancies_row[4] if emp_discrepancies_row and emp_discrepancies_row[4] is not None else 0,
                    "new_quantity": emp_discrepancies_row[5] if emp_discrepancies_row and emp_discrepancies_row[5] is not None else 0,
                    "price_change": emp_discrepancies_row[6] if emp_discrepancies_row and emp_discrepancies_row[6] is not None else 0
                }

                # Rarely will have duplicate tags with discrepancies so this is fairly inexpensive
                if discrepancy_row["tag_number"] in duplicate_tags_map.get(emp_data_row["emp_number"], []):
                    verify_line_row = fetch_line_data(conn=conn, tag_number=discrepancy_row["tag_number"], upc=discrepancy_row["upc"])
                    line_emp_number = verify_line_row[0] if verify_line_row and verify_line_row[0] is not None else ""
                    # If emp_number is 'ZZ9999', that means it is an added item (0 orig qty) so we attribute it to both counters because both counters missed the item
                    if emp_data_row["emp_number"] != line_emp_number and line_emp_number != "ZZ9999":
                        continue

                emp_data_row["discrepancy_dollars"] += discrepancy_row["price_change"]
                emp_data_row["discrepancies"].append(discrepancy_row)
                discrepancy_tags_set.add(discrepancy_row["tag_number"])

            emp_data_row["discrepancy_tags"] = len(discrepancy_tags_set)
            emp_data_row["discrepancy_percent"] = (emp_data_row["discrepancy_dollars"] / emp_data_row["total_price"] * 100) if emp_data_row["total_price"] > 0 else 0

            emp_data.append(emp_data_row)
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