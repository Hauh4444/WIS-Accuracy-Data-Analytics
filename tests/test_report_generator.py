import pytest
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets
from services.report_generator import generate_accuracy_report

@pytest.fixture
def sample_emp_data():
    return [
        {"employee_id": "E001", "employee_name": "Alice", "total_quantity": 50, "uph": 10},
        {"employee_id": "E002", "employee_name": "Bob", "total_quantity": 80, "uph": 5},
    ]

@pytest.fixture
def sample_team_data():
    return [
        {"department_name": "Finance", "department_number": 2},
        {"department_name": "HR", "department_number": 1},
    ]

@pytest.mark.parametrize("invalid_input", [None, "string", 123, {}])
def test_emp_data_type_validation(invalid_input, sample_team_data):
    with patch.object(QtWidgets.QMessageBox, "critical") as mock_critical:
        generate_accuracy_report(invalid_input, sample_team_data)
        mock_critical.assert_called_once()
        assert "emp_data must be a list of dictionaries" in mock_critical.call_args[0][2]

@pytest.mark.parametrize("invalid_input", [None, "string", 123, {}])
def test_team_data_type_validation(invalid_input, sample_emp_data):
    with patch.object(QtWidgets.QMessageBox, "critical") as mock_critical:
        generate_accuracy_report(sample_emp_data, invalid_input)
        mock_critical.assert_called_once()
        assert "team_data must be a list of dictionaries" in mock_critical.call_args[0][2]

def test_template_files_missing(sample_emp_data, sample_team_data):
    with patch("pathlib.Path.exists", side_effect=[False, True]), \
         patch.object(QtWidgets.QMessageBox, "critical") as mock_critical:
        generate_accuracy_report(sample_emp_data, sample_team_data)
        mock_critical.assert_called_once()
        assert "emp_report.html template not found" in mock_critical.call_args[0][2]

def test_pdf_generation_error(sample_emp_data, sample_team_data):
    with patch("services.report_generator.Path.exists", return_value=True), \
         patch("services.report_generator.Environment.get_template") as mock_get_template, \
         patch("xhtml2pdf.pisa.CreatePDF") as mock_create_pdf, \
         patch.object(QtWidgets.QMessageBox, "critical") as mock_critical:
        mock_get_template.return_value.render.return_value = "<html></html>"
        mock_create_pdf.return_value.err = 1
        generate_accuracy_report(sample_emp_data, sample_team_data)
        mock_critical.assert_called_once()
        assert "An error occurred while generating the PDF" in mock_critical.call_args[0][2]

def test_tempfile_creation_and_webbrowser_open(sample_emp_data, sample_team_data):
    with patch("services.report_generator.Path.exists", return_value=True), \
         patch("services.report_generator.Environment.get_template") as mock_get_template, \
         patch("xhtml2pdf.pisa.CreatePDF") as mock_create_pdf, \
         patch("tempfile.NamedTemporaryFile") as mock_tempfile, \
         patch("webbrowser.open") as mock_web_open:
        mock_get_template.return_value.render.return_value = "<html></html>"
        mock_create_pdf.return_value.err = 0
        fake_file = MagicMock()
        fake_file.name = "/tmp/fake.pdf"
        mock_tempfile.return_value.__enter__.return_value = fake_file
        generate_accuracy_report(sample_emp_data, sample_team_data)
        mock_web_open.assert_called_once_with(f"file://{fake_file.name}")

def test_tempfile_not_created(sample_emp_data, sample_team_data):
    with patch("services.report_generator.Path.exists", side_effect=[True, True, False]), \
         patch("services.report_generator.Environment.get_template") as mock_get_template, \
         patch("xhtml2pdf.pisa.CreatePDF") as mock_create_pdf, \
         patch("tempfile.NamedTemporaryFile") as mock_tempfile, \
         patch.object(QtWidgets.QMessageBox, "critical") as mock_critical:
        mock_get_template.return_value.render.return_value = "<html></html>"
        mock_create_pdf.return_value.err = 0
        fake_file = MagicMock()
        fake_file.name = "/tmp/fake.pdf"
        mock_tempfile.return_value.__enter__.return_value = fake_file
        generate_accuracy_report(sample_emp_data, sample_team_data)
        mock_critical.assert_called_once()
        assert "Failed to create temporary PDF file" in mock_critical.call_args[0][2]

def test_full_flow_no_exceptions(sample_emp_data, sample_team_data):
    with patch("services.report_generator.Path.exists", return_value=True), \
         patch("services.report_generator.Environment.get_template") as mock_get_template, \
         patch("xhtml2pdf.pisa.CreatePDF") as mock_create_pdf, \
         patch("tempfile.NamedTemporaryFile") as mock_tempfile, \
         patch("webbrowser.open") as mock_web_open:
        mock_get_template.return_value.render.return_value = "<html></html>"
        mock_create_pdf.return_value.err = 0
        fake_file = MagicMock()
        fake_file.name = "/tmp/fake.pdf"
        mock_tempfile.return_value.__enter__.return_value = fake_file
        generate_accuracy_report(sample_emp_data, sample_team_data)
        mock_web_open.assert_called_once_with(f"file://{fake_file.name}")
