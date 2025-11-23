import pytest
from unittest.mock import MagicMock, patch
from PyQt6 import QtWidgets, QtCore

from views.emp_hours_input_window import EmpHoursInputWindow


@pytest.fixture
def sample_data():
    store_data = {"store": "Store 123", "print_date": "11/23/2025", "store_address": "123 Main St"}
    emp_data = [
        {"emp_number": "E001", "emp_name": "Alice", "total_quantity": 100, "hours": 0},
        {"emp_number": "E002", "emp_name": "Bob", "total_quantity": 200, "hours": 0},
    ]
    zone_data = [{"zone_id": "Z1", "total_quantity": 300}]
    return store_data, emp_data, zone_data


@pytest.fixture
def qt_app(qtbot):
    """Ensure a QApplication instance exists."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app


def test_create_emp_hour_input_row_creates_widgets(sample_data):
    emp = sample_data[1][0]
    row_widget = EmpHoursInputWindow.create_emp_hour_input_row(emp)

    assert hasattr(row_widget, "txt_hours")
    assert hasattr(row_widget, "label_id")
    assert hasattr(row_widget, "label_name")
    assert row_widget.label_id.text() == emp["emp_number"]
    assert row_widget.label_name.text() == emp["emp_name"]
    assert row_widget.txt_hours.text() == str(emp.get("hours", ""))


@patch("emp_hours_window.get_storage_db_connection")
@patch("emp_hours_window.save_local_data")
@patch("emp_hours_window.generate_accuracy_report")
def test_print_report_updates_emp_data(mock_generate, mock_save, mock_conn, sample_data, qt_app, qtbot):
    store_data, emp_data, zone_data = sample_data
    mock_conn.return_value = MagicMock()

    window = EmpHoursInputWindow(store_data, emp_data, zone_data)
    qtbot.addWidget(window)

    for row_widget, hours in zip(window.rows_widgets, [5, 10]):
        row_widget.txt_hours.setText(str(hours))
        qtbot.keyClicks(row_widget.txt_hours, str(hours))
        qtbot.keyPress(row_widget.txt_hours, QtCore.Qt.Key.Key_Return)

    window.print_report()

    assert emp_data[0]["hours"] == 5
    assert emp_data[0]["uph"] == 100 / 5
    assert emp_data[1]["hours"] == 10
    assert emp_data[1]["uph"] == 200 / 10

    mock_save.assert_called_once()
    mock_generate.assert_called_once()


@patch("emp_hours_window.get_storage_db_connection")
def test_print_report_no_connection_closes_window(mock_conn, sample_data, qt_app, qtbot):
    store_data, emp_data, zone_data = sample_data
    mock_conn.return_value = None

    window = EmpHoursInputWindow(store_data, emp_data, zone_data)
    qtbot.addWidget(window)

    window.print_report()
    assert not window.isVisible()


def test_print_report_empty_employee_list(sample_data, qt_app, qtbot):
    store_data, emp_data, zone_data = sample_data
    window = EmpHoursInputWindow(store_data, [], zone_data)
    qtbot.addWidget(window)

    with patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        window.print_report()
        mock_warning.assert_called_once_with(window, "No Data", "No employee data available to print.")


def test_row_input_focus_chain(sample_data, qt_app, qtbot):
    """Test that hitting return moves focus to the next input."""
    store_data, emp_data, zone_data = sample_data
    window = EmpHoursInputWindow(store_data, emp_data, zone_data)
    qtbot.addWidget(window)

    first_row = window.rows_widgets[0]
    second_row = window.rows_widgets[1]

    first_row.txt_hours.setFocus()
    qtbot.keyPress(first_row.txt_hours, QtCore.Qt.Key.Key_Return)

    assert second_row.txt_hours.hasFocus()
