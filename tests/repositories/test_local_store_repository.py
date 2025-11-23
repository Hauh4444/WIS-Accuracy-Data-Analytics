import pytest
from unittest.mock import MagicMock
import pyodbc

import repositories.local_store_repository as repo


@pytest.fixture
def mock_cursor():
    """Fixture for a mocked pyodbc cursor."""
    cursor = MagicMock()
    cursor.fetchone.return_value = ('2025-01-01 10:00:00', 'Store A', '123 Main St')
    cursor.fetchall.return_value = [
        ('2025-01-01 10:00:00',),
        ('2025-02-01 10:00:00',)
    ]
    return cursor


@pytest.fixture
def mock_conn(mock_cursor):
    """Fixture for a mocked pyodbc connection returning a mock cursor."""
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = mock_cursor
    return conn


def test_fetch_inventory_data_returns_row(mock_conn, mock_cursor):
    """Test that fetch_inventory_data returns a single inventory row."""
    store_number = "001"
    result = repo.fetch_inventory_data(mock_conn, store_number)

    mock_conn.cursor.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_cursor.execute.assert_called_once_with(mock_cursor.execute.call_args[0][0], (store_number,))
    assert result == mock_cursor.fetchone.return_value


def test_fetch_inventory_data_no_row(mock_conn, mock_cursor):
    """Test that fetch_inventory_data returns None if no row exists."""
    mock_cursor.fetchone.return_value = None
    result = repo.fetch_inventory_data(mock_conn, "002")
    assert result is None


def test_fetch_season_inventory_data_returns_rows(mock_conn, mock_cursor):
    """Test that fetch_season_inventory_data returns all rows for the season."""
    result = repo.fetch_season_inventory_data(mock_conn)

    mock_conn.cursor.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_cursor.execute.assert_called_once()
    assert result == mock_cursor.fetchall.return_value


def test_fetch_season_inventory_data_no_rows(mock_conn, mock_cursor):
    """Test that fetch_season_inventory_data returns an empty list if no rows exist."""
    mock_cursor.fetchall.return_value = []
    result = repo.fetch_season_inventory_data(mock_conn)
    assert result == []


def test_fetch_inventory_data_executes_correct_query(mock_conn, mock_cursor):
    """Test that fetch_inventory_data executes the correct SQL query with proper columns and table."""
    store_number = "001"
    repo.fetch_inventory_data(mock_conn, store_number)

    executed_sql = mock_cursor.execute.call_args[0][0]
    inventory_table = repo.InventoryTable().table
    for col in ["job_datetime", "store_name", "store_address", "store_number"]:
        assert col in executed_sql
    assert inventory_table in executed_sql


def test_fetch_season_inventory_data_executes_correct_query(mock_conn, mock_cursor):
    """Test that fetch_season_inventory_data executes the correct seasonal SQL query."""
    repo.fetch_season_inventory_data(mock_conn)

    executed_sql = mock_cursor.execute.call_args[0][0]
    inventory_table = repo.InventoryTable().table
    assert inventory_table in executed_sql
    assert "YEAR(" in executed_sql
    assert "Date()" in executed_sql
    assert "job_datetime" in executed_sql
