"""Employee data loader with inventory accuracy metrics."""
import pyodbc
from PyQt6 import QtWidgets

from repositories import fetch_emp_tags_data, fetch_duplicate_tags_data, fetch_emp_data, fetch_emp_totals_data, fetch_emp_line_totals_data, fetch_emp_discrepancies_data, fetch_line_data


def load_source_emp_data(conn: pyodbc.Connection) -> list[dict] | None:
    """Load employee data with discrepancy calculations.
    
    - Business rule: Only discrepancies >$50 with reason='SERVICE_MISCOUNTED' are counted against the zone.
    - Currently, 'ZZ9999' added items will be credited to whoever counted the tag, except for duplicate tags where we check line by line.
    - Added items will be few and far between so verifying all counts line by line would be too expensive to be worth it.
    - Discrepancies of 'ZZ9999' added items get credited to all counters of a tag

    Args:
        conn: Database connection object

    Returns:
        List of dictionaries containing employee data with totals and discrepancies
        
    Raises:
        ValueError: If connection is invalid or database schema is malformed
        RuntimeError: If critical employee data is missing or corrupted
    """
    try:
        if conn is None:
            raise ValueError("Database connection cannot be None")
        if not hasattr(conn, 'cursor'):
            raise ValueError("Invalid database connection object - missing cursor method")

        emp_data = [] # type: list[dict]

        emp_tags_map = {}
        emp_tags_rows = fetch_emp_tags_data(conn)
        for emp_tags_row in emp_tags_rows:
            if emp_tags_row is None or len(emp_tags_row) != 2:
                raise RuntimeError(f"Invalid emp_tags query result structure - expected 2 columns, got {len(emp_tags_row) if emp_tags_row else None}")

            emp_number = emp_tags_row[0] or ""
            emp_tag = emp_tags_row[1] or ""
            emp_tags_map.setdefault(emp_number, set()).add(emp_tag)

        duplicate_tags_set = set()
        duplicate_tags_rows = fetch_duplicate_tags_data(conn)
        for duplicate_tags_row in duplicate_tags_rows:
            if duplicate_tags_row is None or len(duplicate_tags_row) != 1:
                raise RuntimeError(f"Invalid duplicate_tags query result structure - expected 1 column, got {len(duplicate_tags_row) if duplicate_tags_row else None}")

            emp_tag = duplicate_tags_row[0] or ""
            duplicate_tags_set.add(emp_tag)

        emp_rows = fetch_emp_data(conn)
        for emp_row in emp_rows:
            if emp_row is None or len(emp_row) != 2:
                raise RuntimeError(f"Invalid emp query result structure - expected 2 columns, got {len(emp_row) if emp_row else None}")

            emp_data_row: dict = {
                "emp_number": emp_row[0] or "",
                "emp_name": emp_row[1] or "",
                "total_tags": len(emp_tags_map.get(emp_row[0] or "", set())),
                "total_quantity": 0,
                "total_price": 0.0,
                "tags": emp_tags_map.get(emp_row[0] or "", set()),
                "discrepancy_dollars": 0.0,
                "discrepancy_tags": 0,
                "discrepancy_percent": 0.0,
                "discrepancies": [] # type: list[dict]
            }

            # Fetch totals of non-duplicate tags first, we can check these aggregated via tag totals
            emp_totals_row = fetch_emp_totals_data(conn, tags_filter=",".join(emp_data_row["tags"] - duplicate_tags_set))
            if emp_totals_row is None or len(emp_totals_row) != 2:
                raise RuntimeError(f"Invalid emp_totals query result - expected 2 columns, got {len(emp_totals_row) if emp_totals_row else None}")

            emp_data_row["total_quantity"] = emp_totals_row[0] or 0
            emp_data_row["total_price"] = emp_totals_row[1] or 0

            # Fetch totals of duplicate tags, we must check these line by line to verify employee number
            emp_duplicate_totals_row = fetch_emp_line_totals_data(conn, tags_filter=",".join(duplicate_tags_set), emp_number=emp_data_row["emp_number"])
            if emp_duplicate_totals_row is None or len(emp_duplicate_totals_row) != 2:
                raise RuntimeError(f"Invalid emp_line_totals query result - expected 2 columns, got {len(emp_totals_row) if emp_totals_row else None}")

            emp_data_row["total_quantity"] += emp_duplicate_totals_row[0] or 0
            emp_data_row["total_price"] += emp_duplicate_totals_row[1] or 0

            emp_discrepancies_rows = fetch_emp_discrepancies_data(conn, tags_filter=",".join(emp_data_row["tags"]))
            for emp_discrepancies_row in emp_discrepancies_rows:
                if len(emp_discrepancies_row) != 7:
                    raise RuntimeError(f"Invalid emp_discrepancies query result structure - expected 7 columns, got {len(emp_discrepancies_row) if emp_discrepancies_row else None}")

                discrepancy_row: dict = {
                    "zone_id": emp_discrepancies_row[0] or "",
                    "tag_number": emp_discrepancies_row[1] or "",
                    "upc": emp_discrepancies_row[2] or "",
                    "counted_quantity": emp_discrepancies_row[3] or 0,
                    "new_quantity": emp_discrepancies_row[4] or 0,
                    "price": emp_discrepancies_row[5] or 0.0,
                    "price_change": emp_discrepancies_row[6] or 0.0
                }

                # Will rarely have duplicate tags with discrepancies so this is fairly inexpensive
                if discrepancy_row["tag_number"] in duplicate_tags_set:
                    verify_line_row = fetch_line_data(conn, discrepancy_row["tag_number"], discrepancy_row["upc"])
                    line_emp_number = verify_line_row[0] or ""
                    # An employee number of 'ZZ9999', means added item (0 orig qty) so we attribute the discrepancy to both counters since both counters missed the item
                    if emp_data_row["emp_number"] != line_emp_number and line_emp_number != "ZZ9999": continue

                emp_data_row["discrepancy_dollars"] += discrepancy_row["price_change"]
                emp_data_row["discrepancies"].append(discrepancy_row)

            emp_data_row["discrepancy_tags"] = len({discrepancy["tag_number"] for discrepancy in emp_data_row["discrepancies"]})
            emp_data_row["discrepancy_percent"] = (emp_data_row["discrepancy_dollars"] / emp_data_row["total_price"] * 100) if emp_data_row["total_price"] > 0 else 0

            emp_data.append(emp_data_row)

        return emp_data

    except (pyodbc.Error, pyodbc.DatabaseError) as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Database Error",
            f"A database operation failed while loading employee data and discrepancies.\n\nDetails:\n{str(e)}"
        )
        raise

    except ValueError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Configuration Error",
            f"Invalid database connection or missing required input while preparing employee data.\n\nDetails:\n{str(e)}"
        )
        raise

    except RuntimeError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Data Integrity Error",
            f"Critical employee or discrepancy data was missing or inconsistent during the load process.\n\nDetails:\n{str(e)}"
        )
        raise

    except Exception as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Unexpected Error",
            f"An unexpected failure occurred while loading employee data.\nThis may indicate corrupt input, missing fields, or an unhandled edge case.\n\nDetails:\n{str(e)}"
        )
        raise