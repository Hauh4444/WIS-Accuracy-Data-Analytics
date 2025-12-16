import pytest
from unittest.mock import MagicMock
import pyodbc

import repositories.source_zone_repository as repo


@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    cursor.fetchall.return_value = [('row1',), ('row2',)]
    cursor.fetchone.return_value = ('row',)
    return cursor


@pytest.fixture
def mock_conn(mock_cursor):
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = mock_cursor
    return conn


def test_fetch_zone_data_returns_rows(mock_conn, mock_cursor):
    """Test fetch_zone_data returns list of rows."""
    result = repo.fetch_old_zone_data(mock_conn)
    assert result == mock_cursor.fetchall.return_value
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_fetch_zone_totals_data_returns_row(mock_conn, mock_cursor):
    """Test fetch_zone_totals_data returns a single row for a given zone_id."""
    zone_id = "Z001"
    result = repo.fetch_zone_totals_data(mock_conn, zone_id)
    assert result == mock_cursor.fetchone.return_value
    mock_cursor.execute.assert_called_once_with(mock_cursor.execute.call_args[0][0], (zone_id,))
    mock_cursor.close.assert_called_once()


def test_fetch_zone_discrepancy_totals_data_returns_row(mock_conn, mock_cursor):
    """Test fetch_zone_discrepancy_totals_data returns a single row for a given zone_id."""
    zone_id = "Z001"
    result = repo.fetch_zone_discrepancy_totals_data(mock_conn, zone_id)
    assert result == mock_cursor.fetchone.return_value
    mock_cursor.execute.assert_called_once_with(mock_cursor.execute.call_args[0][0], (zone_id, zone_id))
    mock_cursor.close.assert_called_once()


def test_sql_contains_table_names(mock_conn, mock_cursor):
    """Ensure SQL queries reference the correct table names."""
    repo.fetch_old_zone_data(mock_conn)
    zone_table = repo.ZonesTable().table
    assert zone_table in mock_cursor.execute.call_args[0][0]

    repo.fetch_zone_totals_data(mock_conn, "Z001")
    tag_range_table = repo.TagRangeTable().table
    assert tag_range_table in mock_cursor.execute.call_args[0][0]

    repo.fetch_zone_discrepancy_totals_data(mock_conn, "Z001")
    queue_table = repo.ZoneChangeQueueTable().table
    info_table = repo.ZoneChangeInfoTable().table
    sql = mock_cursor.execute.call_args[0][0]
    assert queue_table in sql and info_table in sql
