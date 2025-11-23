import pytest
from unittest.mock import MagicMock
import pyodbc

import repositories.source_emp_repository as repo


@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    cursor.fetchall.return_value = [('row1',), ('row2',)]
    cursor.fetchone.return_value = ('row',)
    cursor.description = [('col1',), ('col2',)]
    return cursor


@pytest.fixture
def mock_conn(mock_cursor):
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = mock_cursor
    return conn


def test_fetch_emp_tags_data_returns_rows(mock_conn, mock_cursor):
    result = repo.fetch_emp_tags_data(mock_conn)
    assert result == mock_cursor.fetchall.return_value
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_fetch_duplicate_tags_data_returns_rows(mock_conn, mock_cursor):
    result = repo.fetch_duplicate_tags_data(mock_conn)
    assert result == mock_cursor.fetchall.return_value
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_fetch_emp_data_returns_rows(mock_conn, mock_cursor):
    result = repo.fetch_emp_data(mock_conn)
    assert result == mock_cursor.fetchall.return_value
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_fetch_emp_totals_data_returns_row(mock_conn, mock_cursor):
    tags_filter = "1,2,3"
    result = repo.fetch_emp_totals_data(mock_conn, tags_filter)
    assert result == mock_cursor.fetchone.return_value
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_fetch_emp_line_totals_data_returns_row(mock_conn, mock_cursor):
    tags_filter = "1,2,3"
    emp_number = "E001"
    result = repo.fetch_emp_line_totals_data(mock_conn, tags_filter, emp_number)
    assert result == mock_cursor.fetchone.return_value
    mock_cursor.execute.assert_called_once_with(mock_cursor.execute.call_args[0][0], (emp_number,))
    mock_cursor.close.assert_called_once()


def test_fetch_emp_discrepancies_data_returns_rows(mock_conn, mock_cursor):
    tags_filter = "1,2,3"
    result = repo.fetch_emp_discrepancies_data(mock_conn, tags_filter)
    assert result == mock_cursor.fetchall.return_value
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_fetch_line_data_returns_row(mock_conn, mock_cursor):
    tag_number = "T001"
    upc = "123456"
    result = repo.fetch_line_data(mock_conn, tag_number, upc)
    assert result == mock_cursor.fetchone.return_value
    mock_cursor.execute.assert_called_once_with(mock_cursor.execute.call_args[0][0], (tag_number, upc))
    mock_cursor.close.assert_called_once()


def test_sql_contains_table_names(mock_conn, mock_cursor):
    """Ensure that SQL queries contain the correct table names."""
    repo.fetch_emp_tags_data(mock_conn)
    details_table = repo.DetailsTable().table
    assert details_table in mock_cursor.execute.call_args[0][0]

    repo.fetch_duplicate_tags_data(mock_conn)
    dload_table = repo.DLoadErrorsTable().table
    assert dload_table in mock_cursor.execute.call_args[0][0]

    repo.fetch_emp_data(mock_conn)
    emp_table = repo.EmpNamesTable().table
    term_table = repo.TerminalControlTable().table
    sql = mock_cursor.execute.call_args[0][0]
    assert emp_table in sql and term_table in sql
