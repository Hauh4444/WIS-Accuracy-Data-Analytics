import pytest
from unittest.mock import patch, MagicMock
import pyodbc

import services.save_local_data as loader


@pytest.fixture
def mock_conn():
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = MagicMock()
    return conn


@pytest.fixture
def store_data():
    return {"store": "Store 123"}


@pytest.fixture
def emp_data():
    return [{"emp_number": "E001", "emp_name": "Alice"}]


@pytest.fixture
def zone_data():
    return [{"zone_id": "Z001", "zone_description": "Electronics"}]


def test_save_local_data_basic(mock_conn, store_data, emp_data, zone_data):
    with patch("repositories.save_local_data_repository.create_tables_if_not_exists") as mock_create_tables, \
         patch("repositories.save_local_data_repository.check_inventory_exists", return_value=False) as mock_check_inventory, \
         patch("repositories.save_local_data_repository.insert_inventory_data") as mock_insert_inventory, \
         patch("repositories.save_local_data_repository.insert_employee_totals_data") as mock_insert_emp_totals, \
         patch("repositories.save_local_data_repository.insert_employee_data") as mock_insert_emp, \
         patch("repositories.save_local_data_repository.insert_zone_totals_data") as mock_insert_zone_totals, \
         patch("repositories.save_local_data_repository.insert_zone_data") as mock_insert_zone:

        loader.save_local_data(mock_conn, store_data, emp_data, zone_data)

        mock_create_tables.assert_called_once_with(conn=mock_conn)
        mock_check_inventory.assert_called_once_with(mock_conn, store_data)
        mock_insert_inventory.assert_called_once_with(mock_conn, store_data)
        mock_insert_emp_totals.assert_called_once_with(mock_conn, emp_data[0])
        mock_insert_emp.assert_called_once_with(mock_conn, store_data, emp_data[0])
        mock_insert_zone_totals.assert_called_once_with(mock_conn, zone_data[0])
        mock_insert_zone.assert_called_once_with(mock_conn, store_data, zone_data[0])


def test_save_local_data_existing_inventory(mock_conn, store_data, emp_data, zone_data):
    with patch("repositories.save_local_data_repository.create_tables_if_not_exists"), \
         patch("repositories.save_local_data_repository.check_inventory_exists", return_value=True), \
         patch("repositories.save_local_data_repository.update_employee_data") as mock_update_emp, \
         patch("repositories.save_local_data_repository.update_zone_data") as mock_update_zone, \
         patch("repositories.save_local_data_repository.check_employee_totals_exist", return_value=True), \
         patch("repositories.save_local_data_repository.check_zone_totals_exist", return_value=True), \
         patch("repositories.save_local_data_repository.update_employee_totals_data") as mock_update_emp_totals, \
         patch("repositories.save_local_data_repository.update_zone_totals_data") as mock_update_zone_totals:

        loader.save_local_data(mock_conn, store_data, emp_data, zone_data)

        mock_update_emp.assert_called_once()
        mock_update_zone.assert_called_once()
        mock_update_emp_totals.assert_called_once()
        mock_update_zone_totals.assert_called_once()


def test_save_local_data_invalid_conn():
    import PyQt6.QtWidgets as qt
    with patch.object(qt.QMessageBox, "warning") as mock_warning:
        with pytest.raises(ValueError):
            loader.save_local_data(None, {}, [], [])
        with pytest.raises(ValueError):
            loader.save_local_data(object(), {}, [], [])
        assert mock_warning.called
