import pytest
import sys
from unittest.mock import MagicMock, patch
from PyQt6 import QtWidgets

from views.emp_hours_input_window import EmpHoursInputWindow


@pytest.fixture
def q_app():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    yield app
    for widget in app.topLevelWidgets():
        widget.close()
    app.processEvents()


@pytest.fixture
def sample_data():
    store_data = {"store": "Store 123", "print_date": "11/23/2025", "store_address": "123 Main St"}
    emp_data = [
        {"emp_number": "E001", "emp_name": "Alice", "total_quantity": 100, "hours": 0},
        {"emp_number": "E002", "emp_name": "Bob", "total_quantity": 200, "hours": 0},
    ]
    zone_data = [{"zone_id": "Z1", "total_quantity": 300}]
    return store_data, emp_data, zone_data


def test_create_emp_hour_input_row_creates_widgets(sample_data, q_app):
    emp = sample_data[1][0]

    with patch("views.emp_hours_input_window.apply_style"), \
            patch("views.emp_hours_input_window.resource_path", side_effect=lambda x: x):
        row_widget = EmpHoursInputWindow.create_emp_hour_input_row(emp)

        assert hasattr(row_widget, "txt_hours")
        assert hasattr(row_widget, "label_id")
        assert hasattr(row_widget, "label_name")
        assert row_widget.label_id.text() == emp["emp_number"]
        assert row_widget.label_name.text() == emp["emp_name"]
        assert row_widget.txt_hours.text() == str(emp.get("hours", ""))

        row_widget.deleteLater()
        q_app.processEvents()


def test_print_report_updates_emp_data(sample_data, q_app):
    store_data, emp_data, zone_data = sample_data

    with patch("views.emp_hours_input_window.uic.loadUi"), \
            patch("views.emp_hours_input_window.apply_style"), \
            patch("views.emp_hours_input_window.resource_path", side_effect=lambda x: x), \
            patch("views.emp_hours_input_window.center_on_screen"), \
            patch("views.emp_hours_input_window.get_storage_db_connection") as mock_conn, \
            patch("views.emp_hours_input_window.save_local_data") as mock_save, \
            patch("views.emp_hours_input_window.generate_accuracy_report") as mock_generate:
        mock_conn.return_value = MagicMock()

        window = EmpHoursInputWindow.__new__(EmpHoursInputWindow)
        window.__init__ = MagicMock()

        window.store_data = store_data
        window.emp_data = emp_data.copy()
        window.zone_data = zone_data
        window.rows_widgets = []
        window.btnPrint = MagicMock()
        window.btnPrint.clicked.connect = MagicMock()

        for i, emp in enumerate(emp_data):
            mock_row = MagicMock()
            mock_txt_hours = MagicMock(spec=QtWidgets.QLineEdit)
            mock_txt_hours.text.return_value = str([5, 10][i])
            mock_row.txt_hours = mock_txt_hours
            window.rows_widgets.append(mock_row)

        window.close = MagicMock()

        window.print_report()

        assert window.emp_data[0]["hours"] == 5
        assert window.emp_data[0]["uph"] == 100 / 5
        assert window.emp_data[1]["hours"] == 10
        assert window.emp_data[1]["uph"] == 200 / 10

        mock_save.assert_called_once()
        mock_generate.assert_called_once()


def test_print_report_no_connection_closes_window(sample_data, q_app):
    store_data, emp_data, zone_data = sample_data

    with patch("views.emp_hours_input_window.uic.loadUi"), \
            patch("views.emp_hours_input_window.apply_style"), \
            patch("views.emp_hours_input_window.resource_path", side_effect=lambda x: x), \
            patch("views.emp_hours_input_window.center_on_screen"), \
            patch("views.emp_hours_input_window.get_storage_db_connection") as mock_conn:
        mock_conn.return_value = None

        window = EmpHoursInputWindow.__new__(EmpHoursInputWindow)
        window.__init__ = MagicMock()

        window.store_data = store_data
        window.emp_data = emp_data.copy()
        window.zone_data = zone_data
        window.rows_widgets = [MagicMock() for _ in emp_data]
        window.btnPrint = MagicMock()
        window.btnPrint.clicked.connect = MagicMock()
        window.isVisible = MagicMock(return_value=True)
        window.close = MagicMock()

        window.print_report()

        window.close.assert_called_once()


def test_print_report_empty_employee_list(sample_data, q_app):
    store_data, emp_data, zone_data = sample_data

    with patch("views.emp_hours_input_window.uic.loadUi"), \
            patch("views.emp_hours_input_window.apply_style"), \
            patch("views.emp_hours_input_window.resource_path", side_effect=lambda x: x), \
            patch("views.emp_hours_input_window.center_on_screen"):
        window = EmpHoursInputWindow.__new__(EmpHoursInputWindow)
        window.__init__ = MagicMock()

        window.store_data = store_data
        window.emp_data = []
        window.zone_data = zone_data
        window.rows_widgets = []
        window.btnPrint = MagicMock()
        window.btnPrint.clicked.connect = MagicMock()

        with patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
            window.print_report()
            mock_warning.assert_called_once_with(window, "No Data", "No employee data available to print.")


def test_row_input_focus_chain(sample_data, q_app):
    store_data, emp_data, zone_data = sample_data
    emp = emp_data[0]

    with patch("views.emp_hours_input_window.apply_style"), \
            patch("views.emp_hours_input_window.resource_path", side_effect=lambda x: x):
        row_widget = EmpHoursInputWindow.create_emp_hour_input_row(emp)

        txt_hours = row_widget.txt_hours
        focus_next_called = []
        txt_hours.focusNextChild = lambda: focus_next_called.append(True)

        txt_hours.returnPressed.emit()

        assert len(focus_next_called) == 1

        row_widget.deleteLater()
        q_app.processEvents()