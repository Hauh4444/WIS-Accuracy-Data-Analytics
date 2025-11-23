import pytest
from unittest.mock import MagicMock
import pyodbc

import repositories.local_zone_repository as repo


@pytest.fixture
def mock_cursor():
    """Fixture for a mocked pyodbc cursor."""
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        ('Z001', 'Zone A', 10, 5, 100.0, 0.0, 0)
    ]
    return cursor


@pytest.fixture
def mock_conn(mock_cursor):
    """Fixture for a mocked pyodbc connection returning a mock cursor."""
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = mock_cursor
    return conn


def test_fetch_zone_data_returns_rows(mock_conn, mock_cursor):
    """Test that fetch_zone_data returns a list of rows for a given store."""
    store_number = "001"
    result = repo.fetch_zone_data(mock_conn, store_number)

    # Cursor lifecycle
    mock_conn.cursor.assert_called_once()
    mock_cursor.close.assert_called_once()

    # Ensure execute was called with correct store parameter
    assert mock_cursor.execute.call_args[0][1] == (store_number,)

    # Verify returned data
    assert result == mock_cursor.fetchall.return_value


def test_fetch_zone_data_no_rows(mock_conn, mock_cursor):
    """Test fetch_zone_data returns empty list if no rows exist."""
    mock_cursor.fetchall.return_value = []
    result = repo.fetch_zone_data(mock_conn, "002")
    assert result == []


def test_fetch_season_zone_data_returns_rows(mock_conn, mock_cursor):
    """Test that fetch_season_zone_data returns season zone data."""
    result = repo.fetch_season_zone_data(mock_conn)

    mock_conn.cursor.assert_called_once()
    mock_cursor.close.assert_called_once()

    # Ensure execute was called without parameters
    mock_cursor.execute.assert_called_once()
    assert result == mock_cursor.fetchall.return_value


def test_fetch_season_zone_data_no_rows(mock_conn, mock_cursor):
    """Test fetch_season_zone_data returns empty list if no rows exist."""
    mock_cursor.fetchall.return_value = []
    result = repo.fetch_season_zone_data(mock_conn)
    assert result == []


def test_fetch_zone_data_executes_correct_query(mock_conn, mock_cursor):
    """Test that fetch_zone_data executes the correct SQL with proper table and columns."""
    store_number = "001"
    repo.fetch_zone_data(mock_conn, store_number)

    executed_sql = mock_cursor.execute.call_args[0][0]
    zone_table = repo.ZoneTable().table

    for col in [
        "zone_id", "zone_description", "total_tags", "total_quantity",
        "total_price", "discrepancy_dollars", "discrepancy_tags", "store_number"
    ]:
        assert col in executed_sql
    assert zone_table in executed_sql


def test_fetch_season_zone_data_executes_correct_query(mock_conn, mock_cursor):
    """Test that fetch_season_zone_data executes the correct SQL with proper table and columns."""
    repo.fetch_season_zone_data(mock_conn)

    executed_sql = mock_cursor.execute.call_args[0][0]
    zone_totals_table = repo.ZoneTotalsTable().table

    for col in [
        "zone_id", "zone_description", "total_tags", "total_quantity",
        "total_price", "discrepancy_dollars", "discrepancy_tags", "stores"
    ]:
        assert col in executed_sql
    assert zone_totals_table in executed_sql
