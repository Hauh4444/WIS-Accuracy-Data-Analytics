import pytest
from unittest.mock import patch, MagicMock
import pyodbc
from PyQt6 import QtWidgets
from services.save_local_data import save_local_data


@pytest.fixture
def mock_conn():
    conn = MagicMock(spec=pyodbc.Connection)
    conn.cursor.return_value = MagicMock()
    return conn


@pytest.fixture(autouse=True)
def q_app():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    yield app


def test_save_local_data_basic(mock_conn):
    store_data = {"store": "Store 123"}
    emp_data = [{"emp_number": "E001", "emp_name": "Alice", "total_tags": 0, "total_quantity": 0,
                 "total_price": 0.0, "discrepancy_dollars": 0.0, "discrepancy_tags": 0, "hours": 0.0}]
    zone_data = [{"zone_id": "Z001", "zone_description": "Electronics", "total_tags": 0,
                  "total_quantity": 0, "total_price": 0.0, "discrepancy_dollars": 0.0, "discrepancy_tags": 0}]

    with patch.object(QtWidgets.QMessageBox, "warning") as mock_warning, \
         patch("services.save_local_data.create_tables_if_not_exists") as mock_create_tables, \
         patch("services.save_local_data.check_inventory_exists", return_value=False), \
         patch("services.save_local_data.check_employee_totals_exist", return_value=False), \
         patch("services.save_local_data.check_zone_totals_exist", return_value=False), \
         patch("services.save_local_data.insert_inventory_data") as mock_insert_inventory, \
         patch("services.save_local_data.insert_employee_totals_data") as mock_insert_emp_totals, \
         patch("services.save_local_data.insert_employee_data") as mock_insert_emp, \
         patch("services.save_local_data.insert_zone_totals_data") as mock_insert_zone_totals, \
         patch("services.save_local_data.insert_zone_data") as mock_insert_zone, \
         patch("services.save_local_data.update_employee_totals_data") as mock_update_emp_totals, \
         patch("services.save_local_data.update_zone_totals_data") as mock_update_zone_totals:

        save_local_data(mock_conn, store_data, emp_data, zone_data)

        mock_insert_emp_totals.assert_called_once_with(mock_conn, emp_data[0])
        mock_insert_zone_totals.assert_called_once_with(mock_conn, zone_data[0])


def test_save_local_data_existing_inventory(mock_conn):
    store_data = {"store": "Store 123"}
    emp_data = [{"emp_number": "E001", "emp_name": "Alice", "total_tags": 0}]
    zone_data = [{"zone_id": "Z001", "zone_description": "Electronics", "total_tags": 0}]
    with patch.object(QtWidgets.QMessageBox, "warning") as mock_warning, \
         patch("services.save_local_data.create_tables_if_not_exists"), \
         patch("services.save_local_data.check_inventory_exists", return_value=True), \
         patch("services.save_local_data.update_employee_data") as mock_update_emp, \
         patch("services.save_local_data.update_zone_data") as mock_update_zone, \
         patch("services.save_local_data.check_employee_totals_exist", return_value=True), \
         patch("services.save_local_data.check_zone_totals_exist", return_value=True), \
         patch("services.save_local_data.update_employee_totals_data") as mock_update_emp_totals, \
         patch("services.save_local_data.update_zone_totals_data") as mock_update_zone_totals:

        save_local_data(mock_conn, store_data, emp_data, zone_data)

        mock_update_emp.assert_called_once()
        mock_update_zone.assert_called_once()
        mock_update_emp_totals.assert_called_once()
        mock_update_zone_totals.assert_called_once()
        assert not mock_warning.called


def test_save_local_data_zero_totals(mock_conn):
    store_data = {"store": "Store 123"}
    emp_data = [{"emp_number": "E001", "emp_name": "Alice", "total_tags": 0}]
    zone_data = [{"zone_id": "Z001", "zone_description": "Electronics", "total_tags": 0}]
    with patch.object(QtWidgets.QMessageBox, "warning") as mock_warning, \
         patch("services.save_local_data.create_tables_if_not_exists"), \
         patch("services.save_local_data.check_inventory_exists", return_value=False), \
         patch("services.save_local_data.insert_inventory_data"), \
         patch("services.save_local_data.check_employee_totals_exist", return_value=False), \
         patch("services.save_local_data.insert_employee_totals_data") as mock_insert_emp_totals, \
         patch("services.save_local_data.insert_employee_data") as mock_insert_emp, \
         patch("services.save_local_data.check_zone_totals_exist", return_value=False), \
         patch("services.save_local_data.insert_zone_totals_data") as mock_insert_zone_totals, \
         patch("services.save_local_data.insert_zone_data") as mock_insert_zone:

        save_local_data(mock_conn, store_data, emp_data, zone_data)

        mock_insert_emp_totals.assert_called_once()
        mock_insert_emp.assert_called_once()
        mock_insert_zone_totals.assert_called_once()
        mock_insert_zone.assert_called_once()
        assert not mock_warning.called


def test_save_local_data_invalid_conn():
    with patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        with pytest.raises(ValueError):
            save_local_data(None, {}, [], [])
        with pytest.raises(ValueError):
            save_local_data(object(), {}, [], [])
        assert mock_warning.called


def test_save_local_data_db_exception(mock_conn):
    store_data = {"store": "Store 123"}
    emp_data = [{"emp_number": "E001", "emp_name": "Alice", "total_tags": 0}]
    zone_data = [{"zone_id": "Z001", "zone_description": "Electronics", "total_tags": 0}]
    with patch("services.save_local_data.create_tables_if_not_exists", side_effect=pyodbc.DatabaseError("DB fail")), \
         patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        with pytest.raises(pyodbc.DatabaseError):
            save_local_data(mock_conn, store_data, emp_data, zone_data)
        assert mock_warning.called
