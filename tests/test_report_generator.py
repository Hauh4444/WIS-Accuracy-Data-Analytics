import pytest
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from services.report_generator import generate_accuracy_report


class TestReportGenerator:
    """Test cases for accuracy report generation."""

    @pytest.fixture
    def sample_emp_data(self):
        """Sample employee data for testing."""
        return [
            {
                "employee_id": "E001",
                "employee_name": "Alice Johnson",
                "total_quantity": 50,
                "uph": 10,
                "total_discrepancy_dollars": 100.0,
                "total_discrepancy_tags": 2,
                "discrepancy_percent": 5.0
            },
            {
                "employee_id": "E002",
                "employee_name": "Bob Smith",
                "total_quantity": 80,
                "uph": 8,
                "total_discrepancy_dollars": 50.0,
                "total_discrepancy_tags": 1,
                "discrepancy_percent": 2.5
            },
        ]

    @pytest.fixture
    def sample_team_data(self):
        """Sample team data for testing."""
        return [
            {
                "department_name": "Finance",
                "department_number": 101,
                "total_quantity": 100,
                "total_discrepancy_dollars": 150.0,
                "total_discrepancy_tags": 3,
                "discrepancy_percent": 7.5
            },
            {
                "department_name": "Human Resources",
                "department_number": 102,
                "total_quantity": 75,
                "total_discrepancy_dollars": 25.0,
                "total_discrepancy_tags": 1,
                "discrepancy_percent": 1.0
            },
        ]

    @pytest.fixture
    def sample_store_data(self):
        """Sample store data for testing."""
        return {
            "inventory_datetime": "2024-01-15 10:00:00",
            "print_date": "1/15/2024",
            "store": "Test Store #123",
            "print_time": "02:30:45PM",
            "store_address": "123 Test Street, Test City, TS 12345"
        }

    @pytest.mark.parametrize("invalid_input", [None, "string", 123, {}])
    def test_emp_data_type_validation(self, invalid_input, sample_team_data, sample_store_data):
        """Test validation of employee data type."""
        with patch.object(QtWidgets.QMessageBox, "critical") as mock_critical:
            generate_accuracy_report(sample_store_data, invalid_input, sample_team_data)
            mock_critical.assert_called_once()
            assert "emp_data must be a list of dictionaries" in mock_critical.call_args[0][2]

    @pytest.mark.parametrize("invalid_input", [None, "string", 123, {}])
    def test_team_data_type_validation(self, invalid_input, sample_emp_data, sample_store_data):
        """Test validation of team data type."""
        with patch.object(QtWidgets.QMessageBox, "critical") as mock_critical:
            generate_accuracy_report(sample_store_data, sample_emp_data, invalid_input)
            mock_critical.assert_called_once()
            assert "team_data must be a list of dictionaries" in mock_critical.call_args[0][2]

    def test_employee_template_file_missing(self, sample_emp_data, sample_team_data, sample_store_data):
        """Test error handling when employee template file is missing."""
        with patch("pathlib.Path.exists", side_effect=[False, True]), \
             patch.object(QtWidgets.QMessageBox, "critical") as mock_critical:
            generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
            mock_critical.assert_called_once()
            assert "emp_report.html template not found" in mock_critical.call_args[0][2]

    def test_team_template_file_missing(self, sample_emp_data, sample_team_data, sample_store_data):
        """Test error handling when team template file is missing."""
        with patch("pathlib.Path.exists", side_effect=[True, False]), \
             patch.object(QtWidgets.QMessageBox, "critical") as mock_critical:
            generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
            mock_critical.assert_called_once()
            assert "team_report.html template not found" in mock_critical.call_args[0][2]

    def test_pdf_generation_error(self, sample_emp_data, sample_team_data, sample_store_data):
        """Test error handling when PDF generation fails."""
        with patch("services.report_generator.Path.exists", return_value=True), \
             patch("services.report_generator.Environment.get_template") as mock_get_template, \
             patch("xhtml2pdf.pisa.CreatePDF") as mock_create_pdf, \
             patch.object(QtWidgets.QMessageBox, "critical") as mock_critical:
            
            mock_get_template.return_value.render.return_value = "<html></html>"
            mock_create_pdf.return_value.err = 1
            
            generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
            
            mock_critical.assert_called_once()
            assert "An error occurred while generating the PDF" in mock_critical.call_args[0][2]

    def test_successful_pdf_generation(self, sample_emp_data, sample_team_data, sample_store_data):
        """Test successful PDF generation and browser opening."""
        with patch("services.report_generator.Path.exists", return_value=True), \
             patch("services.report_generator.Environment.get_template") as mock_get_template, \
             patch("xhtml2pdf.pisa.CreatePDF") as mock_create_pdf, \
             patch("tempfile.NamedTemporaryFile") as mock_tempfile, \
             patch("webbrowser.open") as mock_web_open:
            
            mock_get_template.return_value.render.return_value = "<html></html>"
            mock_create_pdf.return_value.err = 0
            
            fake_file = MagicMock()
            fake_file.name = "/tmp/test_report.pdf"
            mock_tempfile.return_value.__enter__.return_value = fake_file
            
            generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
            
            mock_web_open.assert_called_once_with(f"file://{fake_file.name}")

    def test_tempfile_creation_failure(self, sample_emp_data, sample_team_data, sample_store_data):
        """Test error handling when temporary file creation fails."""
        with patch("services.report_generator.Path.exists", side_effect=[True, True, False]), \
             patch("services.report_generator.Environment.get_template") as mock_get_template, \
             patch("xhtml2pdf.pisa.CreatePDF") as mock_create_pdf, \
             patch("tempfile.NamedTemporaryFile") as mock_tempfile, \
             patch.object(QtWidgets.QMessageBox, "critical") as mock_critical:
            
            mock_get_template.return_value.render.return_value = "<html></html>"
            mock_create_pdf.return_value.err = 0
            
            fake_file = MagicMock()
            fake_file.name = "/tmp/test_report.pdf"
            mock_tempfile.return_value.__enter__.return_value = fake_file
            
            generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
            
            mock_critical.assert_called_once()
            assert "Failed to create temporary PDF file" in mock_critical.call_args[0][2]

    def test_template_rendering_with_data(self, sample_emp_data, sample_team_data, sample_store_data):
        """Test that templates are rendered with correct data."""
        with patch("services.report_generator.Path.exists", return_value=True), \
             patch("services.report_generator.Environment.get_template") as mock_get_template, \
             patch("xhtml2pdf.pisa.CreatePDF") as mock_create_pdf, \
             patch("tempfile.NamedTemporaryFile") as mock_tempfile, \
             patch("webbrowser.open"):
            
            mock_template = MagicMock()
            mock_get_template.return_value = mock_template
            mock_template.render.return_value = "<html></html>"
            mock_create_pdf.return_value.err = 0
            
            fake_file = MagicMock()
            fake_file.name = "/tmp/test_report.pdf"
            mock_tempfile.return_value.__enter__.return_value = fake_file
            
            generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
            
            assert mock_template.render.called

    def test_empty_data_handling(self, sample_store_data):
        """Test handling of empty data lists."""
        with patch("services.report_generator.Path.exists", return_value=True), \
             patch("services.report_generator.Environment.get_template") as mock_get_template, \
             patch("xhtml2pdf.pisa.CreatePDF") as mock_create_pdf, \
             patch("tempfile.NamedTemporaryFile") as mock_tempfile, \
             patch("webbrowser.open"):
            
            mock_get_template.return_value.render.return_value = "<html></html>"
            mock_create_pdf.return_value.err = 0
            
            fake_file = MagicMock()
            fake_file.name = "/tmp/test_report.pdf"
            mock_tempfile.return_value.__enter__.return_value = fake_file
            
            generate_accuracy_report(sample_store_data, [], [])
            
            assert mock_get_template.return_value.render.called

    def test_large_data_handling(self, sample_emp_data, sample_team_data, sample_store_data):
        """Test handling of large datasets."""
        large_emp_data = sample_emp_data * 100
        large_team_data = sample_team_data * 50
        
        with patch("services.report_generator.Path.exists", return_value=True), \
             patch("services.report_generator.Environment.get_template") as mock_get_template, \
             patch("xhtml2pdf.pisa.CreatePDF") as mock_create_pdf, \
             patch("tempfile.NamedTemporaryFile") as mock_tempfile, \
             patch("webbrowser.open"):
            
            mock_get_template.return_value.render.return_value = "<html></html>"
            mock_create_pdf.return_value.err = 0
            
            fake_file = MagicMock()
            fake_file.name = "/tmp/test_report.pdf"
            mock_tempfile.return_value.__enter__.return_value = fake_file
            
            generate_accuracy_report(sample_store_data, large_emp_data, large_team_data)
            
            assert mock_get_template.return_value.render.called