import pytest
from unittest.mock import patch
from PyQt6 import QtWidgets
from views.emp_hours_input_window import EmpHoursInputWindow, create_employee_row


@pytest.fixture(scope="session", autouse=True)
def qapp():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app


@pytest.fixture
def mock_ui(monkeypatch):
    class FakeScrollContents(QtWidgets.QWidget):
        def __init__(self):
            super().__init__()
            self._layout = QtWidgets.QVBoxLayout(self)

        def layout(self):
            return self._layout

        def styleSheet(self):
            return ""

    class FakeWindow:
        def __init__(self):
            self.scrollAreaWidgetContents = FakeScrollContents()
            self.scrollArea = QtWidgets.QScrollArea()
            self.btnPrint = QtWidgets.QPushButton()

    monkeypatch.setattr(
        "views.emp_hours_input_window.uic.loadUi",
        lambda ui_path, self_obj: setattr(self_obj, "__dict__", FakeWindow().__dict__)
    )


def test_create_employee_row_properties(qapp):
    emp = {"employee_id": "E001", "employee_name": "Alice", "hours": 8}
    row = create_employee_row(emp)
    assert row.label_id.text() == "E001"
    assert row.label_name.text() == "Alice"
    assert row.txt_hours.text() == "8"
    assert hasattr(row, "txt_hours")
    assert hasattr(row, "label_id")
    assert hasattr(row, "label_name")


def test_emp_hours_input_window_initialization(mock_ui):
    emp_data = [{"employee_id": "E001", "employee_name": "Alice", "hours": 8, "total_quantity": 80}]
    team_data = [{"department_number": 1, "department_name": "HR"}]
    window = EmpHoursInputWindow(emp_data, team_data)
    assert len(window.rows_widgets) == 1
    row_widget = window.rows_widgets[0]
    assert row_widget.label_name.text() == "Alice"


@patch("views.emp_hours_input_window.generate_accuracy_report")
def test_on_print_clicked_updates_emp_data(mock_report, mock_ui):
    emp_data = [{"employee_id": "E001", "employee_name": "Alice", "hours": 0, "total_quantity": 80}]
    team_data = [{"department_number": 1, "department_name": "HR"}]
    window = EmpHoursInputWindow(emp_data, team_data)
    row = window.rows_widgets[0]
    row.txt_hours.setText("10")
    window.on_print_clicked()
    assert emp_data[0]["hours"] == 10.0
    assert emp_data[0]["uph"] == 8.0
    mock_report.assert_called_once_with(emp_data=emp_data, team_data=team_data)


@patch("views.emp_hours_input_window.generate_accuracy_report")
def test_on_print_clicked_non_numeric_hours(mock_report, mock_ui):
    emp_data = [{"employee_id": "E002", "employee_name": "Bob", "hours": 0, "total_quantity": 50}]
    team_data = [{"department_number": 2, "department_name": "Finance"}]
    window = EmpHoursInputWindow(emp_data, team_data)
    row = window.rows_widgets[0]
    row.txt_hours.setText("abc")
    window.on_print_clicked()
    assert emp_data[0]["hours"] == 0.0
    assert emp_data[0]["uph"] == 0
    mock_report.assert_called_once_with(emp_data=emp_data, team_data=team_data)


@patch("views.emp_hours_input_window.generate_accuracy_report")
def test_on_print_clicked_empty_emp_data(mock_report, mock_ui):
    emp_data = []
    team_data = [{"department_number": 1, "department_name": "HR"}]
    window = EmpHoursInputWindow(emp_data, team_data)
    with patch("views.emp_hours_input_window.QtWidgets.QMessageBox.warning") as mock_warning:
        window.on_print_clicked()
        mock_warning.assert_called_once()
    mock_report.assert_not_called()


def test_apply_scrollbar_style_file_not_exists(mock_ui):
    emp_data = [{"employee_id": "E001", "employee_name": "Alice", "hours": 8, "total_quantity": 80}]
    team_data = [{"department_number": 1, "department_name": "HR"}]
    window = EmpHoursInputWindow(emp_data, team_data)
    window.apply_scrollbar_style()
    assert isinstance(window.scrollArea.styleSheet(), str)


def test_center_on_screen_moves_window(mock_ui):
    emp_data = [{"employee_id": "E001", "employee_name": "Alice", "hours": 8, "total_quantity": 80}]
    team_data = [{"department_number": 1, "department_name": "HR"}]
    window = EmpHoursInputWindow(emp_data, team_data)
    window.center_on_screen()
    pos = window.pos()
    assert pos.x() >= 0 and pos.y() >= 0
