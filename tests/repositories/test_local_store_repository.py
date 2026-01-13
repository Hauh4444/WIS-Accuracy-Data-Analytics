import pytest
import pyodbc
from dataclasses import fields
from unittest.mock import MagicMock

import repositories.local_store_repository as repo
import models.local_models as models


@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    cursor.fetchone.return_value = ('2025-01-01 10:00:00', 'Store A', '123 Main St')
    cursor.fetchall.return_value = [
        ('2025-01-01 10:00:00',),
        ('2025-02-01 10:00:00',)
    ]
    return cursor


@pytest.fixture
def mock_conn(mock_cursor):
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = mock_cursor
    return conn


def test_fetch_old_inventory_data_returns_row(mock_conn, mock_cursor):
    result = repo.fetch_old_inventory_data(mock_conn, "001")
    mock_conn.cursor.assert_called_once()
    mock_cursor.close.assert_called_once()
    assert mock_cursor.execute.call_args[0][1] == ("001",)
    assert result == mock_cursor.fetchone.return_value


def test_fetch_old_inventory_data_no_row(mock_conn, mock_cursor):
    mock_cursor.fetchone.return_value = None
    result = repo.fetch_old_inventory_data(mock_conn, "002")
    assert result is None


def test_fetch_aggregate_inventory_data_returns_rows(mock_conn, mock_cursor):
    result = repo.fetch_aggregate_inventory_data(mock_conn)
    mock_conn.cursor.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_cursor.execute.assert_called_once()
    assert result == mock_cursor.fetchall.return_value


def test_fetch_aggregate_inventory_data_no_rows(mock_conn, mock_cursor):
    mock_cursor.fetchall.return_value = []
    result = repo.fetch_aggregate_inventory_data(mock_conn)
    assert result == []


def test_fetch_old_inventory_data_executes_correct_query(mock_conn, mock_cursor):
    repo.fetch_old_inventory_data(mock_conn, "001")
    executed_sql = mock_cursor.execute.call_args[0][0]

    inventory = models.InventoryTable()
    for field in fields(inventory):
        if field.name != "table":
            assert getattr(inventory, field.name) in executed_sql
    assert inventory.table in executed_sql


def test_fetch_aggregate_inventory_data_executes_correct_query(mock_conn, mock_cursor):
    repo.fetch_aggregate_inventory_data(mock_conn)
    executed_sql = mock_cursor.execute.call_args[0][0]

    inventory = models.InventoryTable()
    assert inventory.table in executed_sql
    assert inventory.job_datetime in executed_sql
    assert "YEAR(" in executed_sql
    assert "Date()" in executed_sql
