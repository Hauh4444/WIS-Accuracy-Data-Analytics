"""Tests for employee hours input window functionality."""

import pytest
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from views.emp_hours_input_window import EmpHoursInputWindow


@pytest.fixture(scope="session", autouse=True)
def qapp():
    """Create QApplication instance for testing."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app


@pytest.fixture
def mock_ui(monkeypatch):
    """Mock UI components for testing."""
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


class TestCreateEmployeeRow:
    """Test cases for employee row creation."""

    def test_create_employee_row_properties(self, mock_ui):
        """Test that employee row is created with correct properties."""
        emp = {"employee_id": "E001", "employee_name": "Alice Johnson", "hours": 8}
        emp_data = [emp]
        team_data = [{"department_number": 1, "department_name": "HR"}]
        
        window = EmpHoursInputWindow(emp_data, team_data)
        row = window.rows_widgets[0]
        
        assert row.label_id.text() == "E001"
        assert row.label_name.text() == "Alice Johnson"
        assert row.txt_hours.text() == "8"
        assert hasattr(row, "txt_hours")
        assert hasattr(row, "label_id")
        assert hasattr(row, "label_name")

    def test_create_employee_row_with_zero_hours(self, mock_ui):
        """Test employee row creation with zero hours."""
        emp = {"employee_id": "E002", "employee_name": "Bob Smith", "hours": 0}
        emp_data = [emp]
        team_data = [{"department_number": 1, "department_name": "HR"}]
        
        window = EmpHoursInputWindow(emp_data, team_data)
        row = window.rows_widgets[0]
        
        assert row.label_id.text() == "E002"
        assert row.label_name.text() == "Bob Smith"
        assert row.txt_hours.text() == "0"

    def test_create_employee_row_with_decimal_hours(self, mock_ui):
        """Test employee row creation with decimal hours."""
        emp = {"employee_id": "E003", "employee_name": "Charlie Brown", "hours": 7.5}
        emp_data = [emp]
        team_data = [{"department_number": 1, "department_name": "HR"}]
        
        window = EmpHoursInputWindow(emp_data, team_data)
        row = window.rows_widgets[0]
        
        assert row.label_id.text() == "E003"
        assert row.label_name.text() == "Charlie Brown"
        assert row.txt_hours.text() == "7.5"


class TestEmpHoursInputWindow:
    """Test cases for the main employee hours input window."""

    def test_window_initialization(self, mock_ui):
        """Test that window initializes properly with employee data."""
        emp_data = [
            {"employee_id": "E001", "employee_name": "Alice Johnson", "hours": 8, "total_quantity": 80}
        ]
        team_data = [
            {"department_number": 1, "department_name": "Human Resources"}
        ]
        
        window = EmpHoursInputWindow(emp_data, team_data)
        
        assert len(window.rows_widgets) == 1
        row_widget = window.rows_widgets[0]
        assert row_widget.label_name.text() == "Alice Johnson"

    def test_multiple_employees_initialization(self, mock_ui):
        """Test window initialization with multiple employees."""
        emp_data = [
            {"employee_id": "E001", "employee_name": "Alice Johnson", "hours": 8, "total_quantity": 80},
            {"employee_id": "E002", "employee_name": "Bob Smith", "hours": 6, "total_quantity": 60},
            {"employee_id": "E003", "employee_name": "Charlie Brown", "hours": 7, "total_quantity": 70}
        ]
        team_data = [
            {"department_number": 1, "department_name": "Human Resources"}
        ]
        
        window = EmpHoursInputWindow(emp_data, team_data)
        
        assert len(window.rows_widgets) == 3
        assert window.rows_widgets[0].label_name.text() == "Alice Johnson"
        assert window.rows_widgets[1].label_name.text() == "Bob Smith"
        assert window.rows_widgets[2].label_name.text() == "Charlie Brown"

    @patch("views.emp_hours_input_window.generate_accuracy_report")
    def test_print_clicked_updates_emp_data(self, mock_report, mock_ui):
        """Test that print button updates employee data correctly."""
        emp_data = [
            {"employee_id": "E001", "employee_name": "Alice Johnson", "hours": 0, "total_quantity": 80}
        ]
        team_data = [
            {"department_number": 1, "department_name": "Human Resources"}
        ]
        
        window = EmpHoursInputWindow(emp_data, team_data)
        row = window.rows_widgets[0]
        row.txt_hours.setText("10")
        
        window.on_print_clicked()
        
        assert emp_data[0]["hours"] == 10.0
        assert emp_data[0]["uph"] == 8.0
        mock_report.assert_called_once_with(emp_data=emp_data, team_data=team_data)

    @patch("views.emp_hours_input_window.generate_accuracy_report")
    def test_print_clicked_non_numeric_hours(self, mock_report, mock_ui):
        """Test handling of non-numeric hours input."""
        emp_data = [
            {"employee_id": "E002", "employee_name": "Bob Smith", "hours": 0, "total_quantity": 50}
        ]
        team_data = [
            {"department_number": 2, "department_name": "Finance"}
        ]
        
        window = EmpHoursInputWindow(emp_data, team_data)
        row = window.rows_widgets[0]
        row.txt_hours.setText("abc")
        
        window.on_print_clicked()
        
        assert emp_data[0]["hours"] == 0.0
        assert emp_data[0]["uph"] == 0
        mock_report.assert_called_once_with(emp_data=emp_data, team_data=team_data)

    @patch("views.emp_hours_input_window.generate_accuracy_report")
    def test_print_clicked_empty_hours(self, mock_report, mock_ui):
        """Test handling of empty hours input."""
        emp_data = [
            {"employee_id": "E003", "employee_name": "Charlie Brown", "hours": 0, "total_quantity": 60}
        ]
        team_data = [
            {"department_number": 3, "department_name": "Engineering"}
        ]
        
        window = EmpHoursInputWindow(emp_data, team_data)
        row = window.rows_widgets[0]
        row.txt_hours.setText("")
        
        window.on_print_clicked()
        
        assert emp_data[0]["hours"] == 0.0
        assert emp_data[0]["uph"] == 0
        mock_report.assert_called_once_with(emp_data=emp_data, team_data=team_data)

    @patch("views.emp_hours_input_window.generate_accuracy_report")
    def test_print_clicked_empty_emp_data(self, mock_report, mock_ui):
        """Test handling when no employee data is available."""
        emp_data = []
        team_data = [
            {"department_number": 1, "department_name": "Human Resources"}
        ]
        
        window = EmpHoursInputWindow(emp_data, team_data)
        
        with patch("views.emp_hours_input_window.QtWidgets.QMessageBox.warning") as mock_warning:
            window.on_print_clicked()
            mock_warning.assert_called_once()
        
        mock_report.assert_not_called()

    @patch("views.emp_hours_input_window.generate_accuracy_report")
    def test_print_clicked_decimal_hours(self, mock_report, mock_ui):
        """Test handling of decimal hours input."""
        emp_data = [
            {"employee_id": "E004", "employee_name": "Diana Prince", "hours": 0, "total_quantity": 100}
        ]
        team_data = [
            {"department_number": 4, "department_name": "Marketing"}
        ]
        
        window = EmpHoursInputWindow(emp_data, team_data)
        row = window.rows_widgets[0]
        row.txt_hours.setText("7.5")
        
        window.on_print_clicked()
        
        assert emp_data[0]["hours"] == 7.5
        assert emp_data[0]["uph"] == pytest.approx(13.33, rel=1e-2)
        mock_report.assert_called_once_with(emp_data=emp_data, team_data=team_data)

    @patch("views.emp_hours_input_window.generate_accuracy_report")
    def test_print_clicked_zero_quantity(self, mock_report, mock_ui):
        """Test handling when total quantity is zero."""
        emp_data = [
            {"employee_id": "E005", "employee_name": "Eve Adams", "hours": 0, "total_quantity": 0}
        ]
        team_data = [
            {"department_number": 5, "department_name": "Operations"}
        ]
        
        window = EmpHoursInputWindow(emp_data, team_data)
        row = window.rows_widgets[0]
        row.txt_hours.setText("8")
        
        window.on_print_clicked()
        
        assert emp_data[0]["hours"] == 8.0
        assert emp_data[0]["uph"] == 0
        mock_report.assert_called_once_with(emp_data=emp_data, team_data=team_data)

    def test_apply_scrollbar_style_file_not_exists(self, mock_ui):
        """Test scrollbar style application when file doesn't exist."""
        emp_data = [
            {"employee_id": "E001", "employee_name": "Alice Johnson", "hours": 8, "total_quantity": 80}
        ]
        team_data = [
            {"department_number": 1, "department_name": "Human Resources"}
        ]
        
        window = EmpHoursInputWindow(emp_data, team_data)
        
        with patch("pathlib.Path.exists", return_value=False):
            window.apply_scrollbar_style()
        
        assert isinstance(window.scrollArea.styleSheet(), str)

    def test_center_on_screen_moves_window(self, mock_ui):
        """Test that center_on_screen properly positions the window."""
        emp_data = [
            {"employee_id": "E001", "employee_name": "Alice Johnson", "hours": 8, "total_quantity": 80}
        ]
        team_data = [
            {"department_number": 1, "department_name": "Human Resources"}
        ]
        
        window = EmpHoursInputWindow(emp_data, team_data)
        window.center_on_screen()
        
        pos = window.pos()
        assert pos.x() >= 0 and pos.y() >= 0

    def test_center_on_screen_no_screen(self, mock_ui):
        """Test center_on_screen handles missing screen gracefully."""
        emp_data = [
            {"employee_id": "E001", "employee_name": "Alice Johnson", "hours": 8, "total_quantity": 80}
        ]
        team_data = [
            {"department_number": 1, "department_name": "Human Resources"}
        ]
        
        window = EmpHoursInputWindow(emp_data, team_data)
        
        with patch.object(QtWidgets.QApplication, 'primaryScreen', return_value=None):
            window.center_on_screen()
            # Should not raise an exception