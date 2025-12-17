import pytest
import pyodbc
from unittest.mock import MagicMock

import repositories.save_local_data_repository as repo


@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    cursor.fetchone.return_value = ('existing',)
    cursor.tables.return_value = [MagicMock(table_name='dummy')]
    return cursor


@pytest.fixture
def mock_conn(mock_cursor):
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = mock_cursor
    return conn


def test_create_tables_if_not_exists_executes_queries(mock_conn, mock_cursor):
    mock_cursor.tables.return_value = []
    repo.create_tables_if_not_exists(mock_conn)
    assert mock_cursor.execute.call_count == 5
    assert mock_conn.commit.call_count == 5
    mock_cursor.close.assert_called_once()


def test_check_inventory_exists_true(mock_conn, mock_cursor):
    store_data = {"store_number": "001"}
    mock_cursor.fetchone.return_value = ('row',)
    assert repo.check_inventory_exists(mock_conn, store_data) is True
    mock_cursor.execute.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_check_inventory_exists_false(mock_conn, mock_cursor):
    store_data = {"store_number": "001"}
    mock_cursor.fetchone.return_value = None
    assert repo.check_inventory_exists(mock_conn, store_data) is False


def test_insert_inventory_data_executes_insert(mock_conn, mock_cursor):
    store_data = {
        "store_number": "001",
        "store": "Store A",
        "inventory_datetime": "2025-01-01 10:00:00",
        "store_address": "123 Main St"
    }
    repo.insert_inventory_data(mock_conn, store_data)
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_update_employee_data_inserts_if_not_exists(mock_conn, mock_cursor, monkeypatch):
    mock_cursor.fetchone.return_value = None
    store_data = {"store_number": "001"}
    emp_data = {"emp_number": "E001", "emp_name": "John", "total_tags": 5, "total_quantity": 3, "total_price": 100.0,
                "discrepancy_dollars": 0.0, "discrepancy_tags": 0, "hours": 8.0}
    called = {}
    monkeypatch.setattr(repo, "insert_employee_data", lambda conn, store_data, emp_data: called.update({"called": True}))
    result = repo.update_employee_data(mock_conn, store_data, emp_data)
    assert result is None
    assert called.get("called") is True


def test_update_employee_data_updates_existing(mock_conn, mock_cursor):
    store_data = {"store_number": "001"}
    emp_data = {"emp_number": "E001", "emp_name": "John", "total_tags": 5, "total_quantity": 3, "total_price": 100.0,
                "discrepancy_dollars": 0.0, "discrepancy_tags": 0, "hours": 8.0}
    mock_cursor.fetchone.return_value = (store_data["store_number"], emp_data["emp_number"], "John", 2, 1, 50.0, 0.0, 0, 4.0)
    mock_cursor.description = [(col,) for col in ["store_number", "emp_number", "emp_name", "total_tags", "total_quantity",
                                                  "total_price", "discrepancy_dollars", "discrepancy_tags", "hours"]]
    prev_data = repo.update_employee_data(mock_conn, store_data, emp_data)
    assert prev_data["total_tags"] == 2
    assert mock_cursor.execute.call_count >= 2
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_update_employee_totals_data_updates_correctly(mock_conn, mock_cursor):
    prev_emp_data = {"total_tags": 2, "total_quantity": 1, "total_price": 50.0, "discrepancy_dollars": 0.0, "discrepancy_tags": 0, "hours": 4.0}
    emp_data = {"emp_number": "E001", "total_tags": 5, "total_quantity": 3, "total_price": 100.0, "discrepancy_dollars": 0.0,
                "discrepancy_tags": 0, "hours": 8.0}
    repo.update_employee_totals_data(mock_conn, prev_emp_data, emp_data)
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()


def test_update_zone_totals_data_updates_correctly(mock_conn, mock_cursor):
    prev_zone_data = {"total_tags": 2, "total_quantity": 1, "total_price": 50.0, "discrepancy_dollars": 0.0, "discrepancy_tags": 0}
    zone_data = {"zone_id": "Z001", "total_tags": 5, "total_quantity": 3, "total_price": 100.0, "discrepancy_dollars": 0.0, "discrepancy_tags": 0}
    repo.update_zone_totals_data(mock_conn, prev_zone_data, zone_data)
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
