"""Team zone data loader with inventory accuracy metrics."""
import pyodbc
from PyQt6 import QtWidgets

from repositories.team_repository import fetch_zone_data, fetch_zone_totals_data, fetch_zone_discrepancy_totals_data


def load_team_data(conn: pyodbc.Connection) -> list[dict]:
    """Load team zone data with discrepancy calculations.
    
    Business rule: Only discrepancies >$50 with reason='SERVICE_MISCOUNTED' are counted against the team.
    
    Args:
        conn: Database connection object
        
    Returns:
        List of dictionaries containing team data with totals and discrepancies
        
    Raises:
        ValueError: If connection is invalid or database schema is malformed
        RuntimeError: If critical team data is missing or corrupted
    """
    team_data = []
    
    try:
        if conn is None:
            raise ValueError("Database connection cannot be None")
        if not hasattr(conn, 'cursor'):
            raise ValueError("Invalid database connection object - missing cursor method")

        zone_rows = fetch_zone_data(conn=conn)
        for zone_row in zone_rows:
            if len(zone_row) != 2:
                raise RuntimeError(f"Invalid zone query result structure - expected 2 columns, got {len(zone_row) if zone_row else 0}")

            team_data_row = {
                "zone_id": zone_row[0] if zone_row and zone_row[0] is not None else "",
                "zone_description": zone_row[1] if zone_row and zone_row[1] is not None else ""
            }

            zone_totals_row = fetch_zone_totals_data(conn=conn, zone_id=team_data_row["zone_id"])
            if zone_totals_row is None or len(zone_totals_row) != 3:
                raise RuntimeError(f"Invalid zone_totals query result - expected 3 columns, got {len(zone_totals_row) if zone_totals_row else 0}")

            team_data_row["total_tags"] = zone_totals_row[0] if zone_totals_row and zone_totals_row[0] is not None else 0
            team_data_row["total_quantity"] = zone_totals_row[1] if zone_totals_row and zone_totals_row[1] is not None else 0
            team_data_row["total_price"] = zone_totals_row[2] if zone_totals_row and zone_totals_row[2] is not None else 0

            zone_discrepancy_totals_row = fetch_zone_discrepancy_totals_data(conn=conn, zone_id=team_data_row["zone_id"])
            if zone_discrepancy_totals_row is None or len(zone_discrepancy_totals_row) != 2:
                raise RuntimeError(f"Invalid zone_discrepancy_totals query result - expected 2 columns, got {len(zone_discrepancy_totals_row) if zone_discrepancy_totals_row else 0}")

            team_data_row["discrepancy_dollars"] = zone_discrepancy_totals_row[0] if zone_discrepancy_totals_row and zone_discrepancy_totals_row[0] is not None else 0
            team_data_row["discrepancy_tags"] = zone_discrepancy_totals_row[1] if zone_discrepancy_totals_row and zone_discrepancy_totals_row[1] is not None else 0
            team_data_row["discrepancy_percent"] = (team_data_row["discrepancy_dollars"] / team_data_row["total_price"] * 100) if team_data_row["total_price"] > 0 else 0
            
            team_data.append(team_data_row)
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

    return team_data