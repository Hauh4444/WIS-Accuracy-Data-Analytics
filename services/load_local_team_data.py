"""Team data loader with inventory accuracy metrics."""
import pyodbc
from PyQt6 import QtWidgets

from repositories.local_team_repository import fetch_zone_data, fetch_season_zone_data


def load_local_team_data(conn: pyodbc.Connection, store: str | None) -> list[dict]:
    """Load team data with discrepancy calculations.

    Args:
        conn: Database connection object
        store: Store number inputted by user or None if retrieving season stats

    Returns:
        List of dictionaries containing team data with totals and discrepancies

    Raises:
        ValueError: If connection is invalid or database schema is malformed
        RuntimeError: If critical team data is missing or corrupted
    """
    team_data = []  # type: list[dict]

    if conn is None:
        raise ValueError("Database connection cannot be None")
    if not hasattr(conn, 'cursor'):
        raise ValueError("Invalid database connection object - missing cursor method")

    if store:
        zone_rows = fetch_zone_data(conn=conn, store=store)
        for zone_row in zone_rows:
            team_data_row: dict = {
                "zone_id": zone_row[0] if zone_row and zone_row[0] else "",
                "zone_description": zone_row[1] if zone_row and zone_row[1] else "",
                "total_tags": zone_row[2] if zone_row and zone_row[2] else 0,
                "total_quantity": zone_row[3] if zone_row and zone_row[3] else 0,
                "total_price": zone_row[4] if zone_row and zone_row[4] else 0.0,
                "discrepancy_dollars": zone_row[5] if zone_row and zone_row[5] else 0.0,
                "discrepancy_tags": zone_row[6] if zone_row and zone_row[6] else 0
            }
            team_data_row["discrepancy_percent"] = (team_data_row["discrepancy_dollars"] / team_data_row["total_price"] * 100) if team_data_row["total_price"] > 0 else 0
            team_data.append(team_data_row)
    else:
        season_zone_rows = fetch_season_zone_data(conn=conn)
        for season_zone_row in season_zone_rows:
            team_data_row: dict = {
                "zone_id": season_zone_row[0] if season_zone_row and season_zone_row[0] else "",
                "zone_description": season_zone_row[1] if season_zone_row and season_zone_row[1] else "",
                "total_tags": season_zone_row[2] if season_zone_row and season_zone_row[2] else 0,
                "total_quantity": season_zone_row[3] if season_zone_row and season_zone_row[3] else 0,
                "total_price": season_zone_row[4] if season_zone_row and season_zone_row[4] else 0.0,
                "discrepancy_dollars": season_zone_row[5] if season_zone_row and season_zone_row[5] else 0.0,
                "discrepancy_tags": season_zone_row[6] if season_zone_row and season_zone_row[6] else 0,
                "stores": season_zone_row[7] if season_zone_row and season_zone_row[7] else 1
            }
            stores = team_data_row["stores"] or 1
            team_data_row["total_tags"] /= stores
            team_data_row["total_quantity"] /= stores
            team_data_row["total_price"] /= stores
            team_data_row["discrepancy_dollars"] /= stores
            team_data_row["discrepancy_tags"] /= stores
            team_data_row["discrepancy_percent"] = (team_data_row["discrepancy_dollars"] / team_data_row["total_price"] * 100) if team_data_row["total_price"] > 0 else 0
            team_data.append(team_data_row)

    return team_data
