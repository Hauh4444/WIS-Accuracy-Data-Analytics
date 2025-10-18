import pytest
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from views.emp_hours_input_window import EmpHoursInputWindow


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


@pytest.fixture
def sample_store_data():
    return {
        "inventory_datetime": "2024-01-15 10:00:00",
        "print_date": "1/15/2024",
        "store": "Test Store #123",
        "print_time": "02:30:45PM",
        "store_address": "123 Test Street, Test City, TS 12345"
    }


class TestEmpHoursInputWindow:

    def test_window_initialization(self, mock_ui, sample_store_data):
        """Test window initialization with employee data."""
        emp_data = [
            {"employee_number": "E001", "employee_name": "Alice Johnson", "hours": 8, "total_quantity": 80}
        ]
        team_data = [
            {"zone_number": 1, "zone_name": "Human Resources"}
        ]
        
        window = EmpHoursInputWindow(sample_store_data, emp_data, team_data)
        
        assert len(window.rows_widgets) == 1
        row_widget = window.rows_widgets[0]
        assert row_widget.label_name.text() == "Alice Johnson"

    def test_multiple_employees_initialization(self, mock_ui, sample_store_data):
        """Test window initialization with multiple employees."""
        emp_data = [
            {"employee_number": "E001", "employee_name": "Alice Johnson", "hours": 8, "total_quantity": 80},
            {"employee_number": "E002", "employee_name": "Bob Smith", "hours": 6, "total_quantity": 60}
        ]
        team_data = [
            {"zone_number": 1, "zone_name": "Human Resources"}
        ]
        
        window = EmpHoursInputWindow(sample_store_data, emp_data, team_data)
        
        assert len(window.rows_widgets) == 2
        assert window.rows_widgets[0].label_name.text() == "Alice Johnson"
        assert window.rows_widgets[1].label_name.text() == "Bob Smith"

    @patch("views.emp_hours_input_window.generate_accuracy_report")
    def test_print_clicked_updates_emp_data(self, mock_report, mock_ui, sample_store_data):
        """Test print clicked updates employee data with hours and UPH calculations."""
        emp_data = [
            {"employee_number": "E001", "employee_name": "Alice Johnson", "hours": 0, "total_quantity": 80}
        ]
        team_data = [
            {"zone_number": 1, "zone_name": "Human Resources"}
        ]
        
        window = EmpHoursInputWindow(sample_store_data, emp_data, team_data)
        row = window.rows_widgets[0]
        row.txt_hours.setText("10")
        
        window.on_print_clicked()
        
        assert emp_data[0]["hours"] == 10.0
        assert emp_data[0]["uph"] == 8.0
        mock_report.assert_called_once_with(store_data=sample_store_data, emp_data=emp_data, team_data=team_data)

    @patch("views.emp_hours_input_window.generate_accuracy_report")
    def test_print_clicked_invalid_hours_handling(self, mock_report, mock_ui, sample_store_data):
        """Test print clicked with invalid hours input."""
        emp_data = [
            {"employee_number": "E002", "employee_name": "Bob Smith", "hours": 0, "total_quantity": 50}
        ]
        team_data = [
            {"zone_number": 2, "zone_name": "Finance"}
        ]
        
        window = EmpHoursInputWindow(sample_store_data, emp_data, team_data)
        row = window.rows_widgets[0]
        row.txt_hours.setText("abc")  # Invalid input
        
        window.on_print_clicked()
        
        assert emp_data[0]["hours"] == 0.0
        assert emp_data[0]["uph"] == 0
        mock_report.assert_called_once()

    @patch("views.emp_hours_input_window.generate_accuracy_report")
    def test_print_clicked_empty_emp_data_warning(self, mock_report, mock_ui, sample_store_data):
        """Test print clicked with empty employee data shows warning."""
        emp_data = []
        team_data = [
            {"zone_number": 1, "zone_name": "Human Resources"}
        ]
        
        window = EmpHoursInputWindow(sample_store_data, emp_data, team_data)
        
        with patch("views.emp_hours_input_window.QtWidgets.QMessageBox.warning") as mock_warning:
            window.on_print_clicked()
            mock_warning.assert_called_once()
        
        mock_report.assert_not_called()

    @patch("views.emp_hours_input_window.generate_accuracy_report")
    def test_uph_calculation_zero_hours(self, mock_report, mock_ui, sample_store_data):
        """Test UPH calculation with zero hours (should result in UPH = 0)."""
        emp_data = [
            {"employee_number": "E001", "employee_name": "Alice Johnson", "hours": 0, "total_quantity": 80}
        ]
        team_data = []
        
        window = EmpHoursInputWindow(sample_store_data, emp_data, team_data)
        row = window.rows_widgets[0]
        row.txt_hours.setText("0")
        
        window.on_print_clicked()
        
        assert emp_data[0]["hours"] == 0.0
        assert emp_data[0]["uph"] == 0
        mock_report.assert_called_once()

    @patch("views.emp_hours_input_window.generate_accuracy_report")
    def test_uph_calculation_decimal_precision(self, mock_report, mock_ui, sample_store_data):
        """Test UPH calculation with decimal hours precision."""
        emp_data = [
            {"employee_number": "E001", "employee_name": "Alice Johnson", "hours": 0, "total_quantity": 80}
        ]
        team_data = []
        
        window = EmpHoursInputWindow(sample_store_data, emp_data, team_data)
        row = window.rows_widgets[0]
        row.txt_hours.setText("7.5")
        
        window.on_print_clicked()
        
        assert emp_data[0]["hours"] == 7.5
        assert emp_data[0]["uph"] == (80 / 7.5)
        mock_report.assert_called_once()

    def test_center_on_screen_functionality(self, mock_ui, sample_store_data):
        """Test center on screen functionality."""
        emp_data = [
            {"employee_number": "E001", "employee_name": "Alice Johnson", "hours": 8, "total_quantity": 80}
        ]
        team_data = [
            {"zone_number": 1, "zone_name": "Human Resources"}
        ]
        
        window = EmpHoursInputWindow(sample_store_data, emp_data, team_data)
        window.center_on_screen()
        
        pos = window.pos()
        assert pos.x() >= 0 and pos.y() >= 0