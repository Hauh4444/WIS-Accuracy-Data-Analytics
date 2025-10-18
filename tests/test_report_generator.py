import pytest
from unittest.mock import patch, MagicMock

from services.report_generator import generate_accuracy_report


class TestReportGenerator:

    @pytest.fixture
    def sample_emp_data(self):
        return [
            {
                "employee_number": "E001",
                "employee_name": "Alice Johnson",
                "total_quantity": 50,
                "uph": 10,
                "total_discrepancy_dollars": 100.0,
                "total_discrepancy_tags": 2,
                "discrepancy_percent": 5.0
            }
        ]

    @pytest.fixture
    def sample_team_data(self):
        return [
            {
                "zone_name": "Finance",
                "zone_number": 101,
                "total_quantity": 100,
                "total_discrepancy_dollars": 150.0,
                "total_discrepancy_tags": 3,
                "discrepancy_percent": 7.5
            }
        ]

    @pytest.fixture
    def sample_store_data(self):
        return {
            "store": "Test Store #123",
            "store_address": "123 Test Street, Test City, TS 12345",
            "inventory_datetime": "2024-01-15 10:00:00",
            "print_date": "1/15/2024",
            "print_time": "02:30:45PM"
        }

    @patch("services.report_generator.QtWidgets.QMessageBox.critical")
    @pytest.mark.parametrize("invalid_input", [None, "string", 123])
    def test_emp_data_type_validation(self, mock_critical, invalid_input, sample_team_data, sample_store_data):
        """Test emp_data type validation."""
        with pytest.raises(ValueError, match="emp_data and team_data must be lists"):
            generate_accuracy_report(sample_store_data, invalid_input, sample_team_data)
        mock_critical.assert_called_once()

    @patch("services.report_generator.QtWidgets.QMessageBox.critical")
    @pytest.mark.parametrize("invalid_input", [None, "string", 123])
    def test_team_data_type_validation(self, mock_critical, invalid_input, sample_emp_data, sample_store_data):
        """Test team_data type validation."""
        with pytest.raises(ValueError, match="emp_data and team_data must be lists"):
            generate_accuracy_report(sample_store_data, sample_emp_data, invalid_input)
        mock_critical.assert_called_once()

    @patch("services.report_generator.QtWidgets.QMessageBox.critical")
    def test_empty_store_data_validation(self, mock_critical, sample_emp_data, sample_team_data):
        """Test empty store_data validation."""
        with pytest.raises(ValueError, match="store_data cannot be empty or None"):
            generate_accuracy_report({}, sample_emp_data, sample_team_data)
        mock_critical.assert_called_once()

    @patch("services.report_generator.QtWidgets.QMessageBox.critical")
    @patch("services.report_generator.resource_path")
    def test_templates_directory_not_found(self, mock_resource_path, mock_critical, sample_emp_data, sample_team_data, sample_store_data):
        """Test templates directory not found error."""
        mock_resource_path.return_value = None
        
        with pytest.raises(RuntimeError, match="Templates directory not found or invalid"):
            generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
        mock_critical.assert_called_once()