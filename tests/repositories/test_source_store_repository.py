import pytest
import pyodbc
from unittest.mock import MagicMock

import repositories.source_store_repository as repo


@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    cursor.fetchone.return_value = ('2025-01-01 10:00:00', 'Store A', '123 Main St')
    return cursor


@pytest.fixture
def mock_conn(mock_cursor):
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = mock_cursor
    return conn


def test_fetch_wise_data_returns_row(mock_conn, mock_cursor):
    result = repo.fetch_wise_data(mock_conn)
    assert result == ('2025-01-01 10:00:00', 'Store A', '123 Main St')
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_fetch_wise_data_sql_contains_table_name(mock_conn, mock_cursor):
    repo.fetch_wise_data(mock_conn)
    wise_table = repo.WISEInfoTable().table
    executed_sql = mock_cursor.execute.call_args[0][0]
    assert wise_table in executed_sql
