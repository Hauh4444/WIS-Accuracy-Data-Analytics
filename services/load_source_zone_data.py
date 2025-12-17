"""zone zone data loader with inventory accuracy metrics."""
import pyodbc
from PyQt6 import QtWidgets

from repositories import fetch_zone_data, fetch_zone_totals_data, fetch_zone_discrepancy_totals_data


def load_source_zone_data(conn: pyodbc.Connection) -> list[dict] | None:
    """Load zone zone data with discrepancy calculations.
    
    - Business rule: Only discrepancies >$50 with reason='SERVICE_MISCOUNTED' are counted against the zone.
    
    Args:
        conn: Database connection object
        
    Returns:
        List of dictionaries containing zone data with totals and discrepancies
        
    Raises:
        ValueError: If connection is invalid or database schema is malformed
        RuntimeError: If critical zone data is missing or corrupted
    """
    try:
        if conn is None:
            raise ValueError("Database connection cannot be None")
        if not hasattr(conn, 'cursor'):
            raise ValueError("Invalid database connection object - missing cursor method")

        zone_data: list[dict] = []

        zone_rows = fetch_zone_data(conn)
        for zone_row in zone_rows:
            if len(zone_row) != 2:
                raise RuntimeError(f"Invalid zone query result structure - expected 2 columns, got {len(zone_row) if zone_row else None}")

            zone_data_row: dict = {
                "zone_id": zone_row[0] or "",
                "zone_description": zone_row[1] or "",
                "total_tags": 0,
                "total_quantity": 0,
                "total_price": 0.0,
                "discrepancy_dollars": 0.0,
                "discrepancy_tags": 0,
                "discrepancy_percent": 0.0
            }

            zone_totals_row = fetch_zone_totals_data(conn, zone_data_row["zone_id"])
            if zone_totals_row is None or len(zone_totals_row) != 3:
                raise RuntimeError(f"Invalid zone_totals query result - expected 3 columns, got {len(zone_totals_row) if zone_totals_row else None}")

            zone_data_row["total_tags"] = zone_totals_row[0] or 0
            zone_data_row["total_quantity"] = zone_totals_row[1] or 0
            zone_data_row["total_price"] = zone_totals_row[2] or 0

            zone_discrepancy_totals_row = fetch_zone_discrepancy_totals_data(conn, zone_data_row["zone_id"])
            if zone_discrepancy_totals_row is None or len(zone_discrepancy_totals_row) != 2:
                raise RuntimeError(f"Invalid zone_discrepancy_totals query result - expected 2 columns, got {len(zone_discrepancy_totals_row) if zone_discrepancy_totals_row else None}")

            zone_data_row["discrepancy_dollars"] = zone_discrepancy_totals_row[0] or 0
            zone_data_row["discrepancy_tags"] = zone_discrepancy_totals_row[1] or 0
            zone_data_row["discrepancy_percent"] = (zone_data_row["discrepancy_dollars"] / zone_data_row["total_price"] * 100) if zone_data_row["total_price"] > 0 else 0

            zone_data.append(zone_data_row)

        return zone_data

    except (pyodbc.Error, pyodbc.DatabaseError) as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Database Error",
            f"A database operation failed while loading zone zone or discrepancy data.\n\nDetails:\n{str(e)}"
        )
        raise

    except ValueError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Configuration Error",
            f"Invalid database connection or missing required input while preparing zone data.\n\nDetails:\n{str(e)}"
        )
        raise

    except RuntimeError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Data Integrity Error",
            f"Critical zone zone or discrepancy data was missing or inconsistent during the load process.\n\nDetails:\n{str(e)}"
        )
        raise

    except Exception as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Unexpected Error",
            f"An unexpected failure occurred while loading zone data.\nThis may indicate corrupt input, missing fields, or an unhandled edge case.\n\nDetails:\n{str(e)}"
        )
        raise