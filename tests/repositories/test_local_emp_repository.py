import pytest
import pyodbc
from dataclasses import fields
from unittest.mock import MagicMock

import repositories.local_emp_repository as repo
import models.local_models as models


@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    cursor.fetchall.return_value = [
        ("123", "John Doe", 10, 5, 100.0, 0.0, 0, 8.0)
    ]
    return cursor


@pytest.fixture
def mock_conn(mock_cursor):
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = mock_cursor
    return conn


def test_fetch_old_emp_data_returns_rows(mock_conn, mock_cursor):
    result = repo.fetch_old_emp_data(mock_conn, "001")

    mock_conn.cursor.assert_called_once()
    mock_cursor.close.assert_called_once()
    assert mock_cursor.execute.call_args[0][1] == ("001",)
    assert result == mock_cursor.fetchall.return_value


def test_fetch_old_emp_data_with_no_rows(mock_conn, mock_cursor):
    mock_cursor.fetchall.return_value = []

    result = repo.fetch_old_emp_data(mock_conn, "002")

    mock_conn.cursor.assert_called_once()
    mock_cursor.close.assert_called_once()
    assert result == []


def test_fetch_old_emp_data_executes_correct_query(mock_conn, mock_cursor):
    repo.fetch_old_emp_data(mock_conn, "001")

    executed_sql = mock_cursor.execute.call_args[0][0]

    emp = models.EmployeeTable()
    for field in fields(emp):
        assert getattr(emp, field.name) in executed_sql
