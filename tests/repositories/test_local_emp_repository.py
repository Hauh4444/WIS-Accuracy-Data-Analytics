import pytest
from unittest.mock import MagicMock
import pyodbc

import repositories.local_emp_repository as repo


@pytest.fixture
def mock_cursor():
    """Fixture for a mocked pyodbc cursor."""
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        ('123', 'John Doe', 10, 5, 100.0, 0.0, 0, 8.0)
    ]
    return cursor


@pytest.fixture
def mock_conn(mock_cursor):
    """Fixture for a mocked pyodbc connection returning a mock cursor."""
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = mock_cursor
    return conn


def test_fetch_emp_data_returns_rows(mock_conn, mock_cursor):
    """Test that fetch_emp_data returns the expected rows from the database."""
    store_number = "001"

    result = repo.fetch_emp_data(mock_conn, store_number)

    # Verify that the cursor was created and closed
    mock_conn.cursor.assert_called_once()
    mock_cursor.close.assert_called_once()

    # Verify that execute was called with the correct SQL and parameter
    assert mock_cursor.execute.call_args[0][1] == (store_number,)

    # Verify that the function returns the data from fetchall
    assert result == mock_cursor.fetchall.return_value


def test_fetch_emp_data_with_no_rows(mock_conn, mock_cursor):
    """Test that fetch_emp_data returns an empty list if no rows exist."""
    mock_cursor.fetchall.return_value = []

    result = repo.fetch_emp_data(mock_conn, "002")
    assert result == []


def test_fetch_season_emp_data_returns_rows(mock_conn, mock_cursor):
    """Test that fetch_season_emp_data returns the expected seasonal data."""
    result = repo.fetch_season_emp_data(mock_conn)

    # Verify cursor lifecycle
    mock_conn.cursor.assert_called_once()
    mock_cursor.close.assert_called_once()

    # Ensure execute was called once with no parameters
    mock_cursor.execute.assert_called_once_with(mock_cursor.execute.call_args[0][0])

    # Verify result
    assert result == mock_cursor.fetchall.return_value


def test_fetch_season_emp_data_with_no_rows(mock_conn, mock_cursor):
    """Test that fetch_season_emp_data returns an empty list if no rows exist."""
    mock_cursor.fetchall.return_value = []

    result = repo.fetch_season_emp_data(mock_conn)
    assert result == []


def test_fetch_emp_data_executes_correct_query(mock_conn, mock_cursor):
    """Test that fetch_emp_data executes the SQL query with correct table/column names."""
    store_number = "001"

    repo.fetch_emp_data(mock_conn, store_number)

    # Extract the SQL query string
    executed_sql = mock_cursor.execute.call_args[0][0]

    # Ensure table and columns are present in the query
    emp_table = repo.EmployeeTable().table
    assert emp_table in executed_sql
    for col in [
        "emp_number", "emp_name", "total_tags",
        "total_quantity", "total_price", "discrepancy_dollars",
        "discrepancy_tags", "hours", "store_number"
    ]:
        assert col in executed_sql


def test_fetch_season_emp_data_executes_correct_query(mock_conn, mock_cursor):
    """Test that fetch_season_emp_data executes the SQL query with correct table/column names."""
    repo.fetch_season_emp_data(mock_conn)

    executed_sql = mock_cursor.execute.call_args[0][0]

    emp_totals_table = repo.EmployeeTotalsTable().table
    assert emp_totals_table in executed_sql
    for col in [
        "emp_number", "emp_name", "total_tags", "total_quantity",
        "total_price", "discrepancy_dollars", "discrepancy_tags",
        "stores", "hours"
    ]:
        assert col in executed_sql
