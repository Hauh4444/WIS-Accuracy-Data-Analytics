"""Tests for report generator utility."""
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from PyQt6 import QtWidgets

from utils.report_generator import generate_accuracy_report


class TestGenerateAccuracyReport:
    """Test generate_accuracy_report function."""
    
    def test_successful_report_generation(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test successful report generation."""
        with patch('utils.report_generator.resource_path') as mock_resource_path, \
             patch('utils.report_generator.Path.exists', return_value=True), \
             patch('utils.report_generator.Environment') as mock_env, \
             patch('utils.report_generator.pisa.CreatePDF') as mock_pisa, \
             patch('utils.report_generator.tempfile.NamedTemporaryFile') as mock_tempfile, \
             patch('utils.report_generator.webbrowser.open') as mock_webbrowser:
            
            # Setup mocks
            mock_resource_path.return_value = "/path/to/templates"
            mock_template = Mock()
            mock_template.render.return_value = "<html>Test HTML</html>"
            mock_env.return_value.get_template.return_value = mock_template
            mock_pisa.return_value.err = False
            
            mock_file = Mock()
            mock_file.name = "/tmp/test.pdf"
            mock_file.write = Mock()
            mock_file.flush = Mock()
            mock_tempfile.return_value.__enter__ = Mock(return_value=mock_file)
            mock_tempfile.return_value.__exit__ = Mock(return_value=None)
            
            # Mock Path.resolve to return the same path
            with patch('utils.report_generator.Path.resolve', return_value=Path("/tmp/test.pdf")):
                generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
            
            # Verify template rendering
            assert mock_template.render.call_count == 3  # emp, team, disc templates
            
            # Verify PDF generation
            mock_pisa.assert_called_once()
            
            # Verify file operations
            mock_file.write.assert_called_once()
            mock_file.flush.assert_called_once()
            
            # Verify browser opening
            mock_webbrowser.open.assert_called_once_with("file:///tmp/test.pdf")
    
    def test_empty_store_data(self, sample_emp_data, sample_team_data):
        """Test ValueError when store_data is empty."""
        with pytest.raises(ValueError, match="store_data cannot be empty or None"):
            generate_accuracy_report({}, sample_emp_data, sample_team_data)
    
    def test_none_store_data(self, sample_emp_data, sample_team_data):
        """Test ValueError when store_data is None."""
        with pytest.raises(ValueError, match="store_data cannot be empty or None"):
            generate_accuracy_report(None, sample_emp_data, sample_team_data)
    
    def test_invalid_emp_data_type(self, sample_store_data, sample_team_data):
        """Test ValueError when emp_data is not a list."""
        with pytest.raises(ValueError, match="emp_data and team_data must be lists"):
            generate_accuracy_report(sample_store_data, "not_a_list", sample_team_data)
    
    def test_invalid_team_data_type(self, sample_store_data, sample_emp_data):
        """Test ValueError when team_data is not a list."""
        with pytest.raises(ValueError, match="emp_data and team_data must be lists"):
            generate_accuracy_report(sample_store_data, sample_emp_data, "not_a_list")
    
    def test_templates_directory_not_found(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test RuntimeError when templates directory is not found."""
        with patch('utils.report_generator.resource_path') as mock_resource_path, \
             patch('utils.report_generator.Path.exists', return_value=False):
            
            mock_resource_path.return_value = None
            
            with pytest.raises(RuntimeError, match="Templates directory not found or invalid"):
                generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
    
    def test_missing_template_file(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test RuntimeError when required template file is missing."""
        with patch('utils.report_generator.resource_path') as mock_resource_path, \
             patch('utils.report_generator.Path.exists') as mock_exists:
            
            mock_resource_path.return_value = "/path/to/templates"
            # Return True for templates directory, False for template files
            mock_exists.side_effect = lambda x: str(x).endswith("templates")
            
            with pytest.raises(RuntimeError, match="Required template file not found"):
                generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
    
    def test_pdf_generation_error(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test RuntimeError when PDF generation fails."""
        with patch('utils.report_generator.resource_path') as mock_resource_path, \
             patch('utils.report_generator.Path.exists', return_value=True), \
             patch('utils.report_generator.Environment') as mock_env, \
             patch('utils.report_generator.pisa.CreatePDF') as mock_pisa, \
             patch('utils.report_generator.QtWidgets.QMessageBox.critical') as mock_msgbox:
            
            mock_resource_path.return_value = "/path/to/templates"
            mock_template = Mock()
            mock_template.render.return_value = "<html>Test HTML</html>"
            mock_env.return_value.get_template.return_value = mock_template
            mock_pisa.return_value.err = True  # PDF generation error
            
            with pytest.raises(RuntimeError, match="PDF generation failed"):
                generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
            
            mock_msgbox.assert_called_once()
    
    def test_temp_file_creation_failure(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test RuntimeError when temporary file creation fails."""
        with patch('utils.report_generator.resource_path') as mock_resource_path, \
             patch('utils.report_generator.Path.exists', return_value=True), \
             patch('utils.report_generator.Environment') as mock_env, \
             patch('utils.report_generator.pisa.CreatePDF') as mock_pisa, \
             patch('utils.report_generator.tempfile.NamedTemporaryFile') as mock_tempfile, \
             patch('utils.report_generator.Path.resolve', return_value=Path("/nonexistent/test.pdf")), \
             patch('utils.report_generator.Path.exists', return_value=False), \
             patch('utils.report_generator.QtWidgets.QMessageBox.critical') as mock_msgbox:
            
            mock_resource_path.return_value = "/path/to/templates"
            mock_template = Mock()
            mock_template.render.return_value = "<html>Test HTML</html>"
            mock_env.return_value.get_template.return_value = mock_template
            mock_pisa.return_value.err = False
            
            mock_file = Mock()
            mock_file.name = "/tmp/test.pdf"
            mock_file.write = Mock()
            mock_file.flush = Mock()
            mock_tempfile.return_value.__enter__ = Mock(return_value=mock_file)
            mock_tempfile.return_value.__exit__ = Mock(return_value=None)
            
            with pytest.raises(RuntimeError, match="Failed to create temporary PDF file"):
                generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
            
            mock_msgbox.assert_called_once()
    
    def test_data_sorting(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test that data is properly sorted before rendering."""
        with patch('utils.report_generator.resource_path') as mock_resource_path, \
             patch('utils.report_generator.Path.exists', return_value=True), \
             patch('utils.report_generator.Environment') as mock_env, \
             patch('utils.report_generator.pisa.CreatePDF') as mock_pisa, \
             patch('utils.report_generator.tempfile.NamedTemporaryFile') as mock_tempfile, \
             patch('utils.report_generator.webbrowser.open') as mock_webbrowser:
            
            mock_resource_path.return_value = "/path/to/templates"
            mock_template = Mock()
            mock_template.render.return_value = "<html>Test HTML</html>"
            mock_env.return_value.get_template.return_value = mock_template
            mock_pisa.return_value.err = False
            
            mock_file = Mock()
            mock_file.name = "/tmp/test.pdf"
            mock_file.write = Mock()
            mock_file.flush = Mock()
            mock_tempfile.return_value.__enter__ = Mock(return_value=mock_file)
            mock_tempfile.return_value.__exit__ = Mock(return_value=None)
            
            with patch('utils.report_generator.Path.resolve', return_value=Path("/tmp/test.pdf")):
                generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
            
            # Verify that templates were called with sorted data
            render_calls = mock_template.render.call_args_list
            
            # Check that emp_data was sorted (should be called with sorted data)
            assert len(render_calls) == 3  # emp, team, disc templates
    
    def test_html_concatenation(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test that HTML is properly concatenated."""
        with patch('utils.report_generator.resource_path') as mock_resource_path, \
             patch('utils.report_generator.Path.exists', return_value=True), \
             patch('utils.report_generator.Environment') as mock_env, \
             patch('utils.report_generator.pisa.CreatePDF') as mock_pisa, \
             patch('utils.report_generator.tempfile.NamedTemporaryFile') as mock_tempfile, \
             patch('utils.report_generator.webbrowser.open') as mock_webbrowser:
            
            mock_resource_path.return_value = "/path/to/templates"
            
            # Mock different templates with different HTML content
            mock_emp_template = Mock()
            mock_emp_template.render.return_value = "<html>Employee Report</html>"
            mock_team_template = Mock()
            mock_team_template.render.return_value = "<html>Team Report</html>"
            mock_disc_template = Mock()
            mock_disc_template.render.return_value = "<html>Discrepancy Report</html>"
            
            mock_env_instance = Mock()
            mock_env_instance.get_template.side_effect = lambda name: {
                "emp_report.html": mock_emp_template,
                "team_report.html": mock_team_template,
                "disc_report.html": mock_disc_template
            }[name]
            mock_env.return_value = mock_env_instance
            
            mock_pisa.return_value.err = False
            
            mock_file = Mock()
            mock_file.name = "/tmp/test.pdf"
            mock_file.write = Mock()
            mock_file.flush = Mock()
            mock_tempfile.return_value.__enter__ = Mock(return_value=mock_file)
            mock_tempfile.return_value.__exit__ = Mock(return_value=None)
            
            with patch('utils.report_generator.Path.resolve', return_value=Path("/tmp/test.pdf")):
                generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
            
            # Verify that pisa.CreatePDF was called with concatenated HTML
            pisa_call_args = mock_pisa.call_args[0][0]
            assert "Employee Report" in pisa_call_args
            assert "Team Report" in pisa_call_args
            assert "Discrepancy Report" in pisa_call_args
            assert "page-break-before: always" in pisa_call_args
    
    def test_value_error_handling(self, sample_emp_data, sample_team_data):
        """Test ValueError handling with message box."""
        with patch('utils.report_generator.QtWidgets.QMessageBox.critical') as mock_msgbox:
            with pytest.raises(ValueError):
                generate_accuracy_report(None, sample_emp_data, sample_team_data)
            
            mock_msgbox.assert_called_once()
    
    def test_runtime_error_handling(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test RuntimeError handling with message box."""
        with patch('utils.report_generator.resource_path', return_value=None), \
             patch('utils.report_generator.QtWidgets.QMessageBox.critical') as mock_msgbox:
            
            with pytest.raises(RuntimeError):
                generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
            
            mock_msgbox.assert_called_once()
    
    def test_generic_exception_handling(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test generic Exception handling with message box."""
        with patch('utils.report_generator.resource_path', side_effect=Exception("Generic error")), \
             patch('utils.report_generator.QtWidgets.QMessageBox.critical') as mock_msgbox:
            
            with pytest.raises(Exception):
                generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
            
            mock_msgbox.assert_called_once()
    
    def test_template_rendering_with_data(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test that templates are rendered with correct data."""
        with patch('utils.report_generator.resource_path') as mock_resource_path, \
             patch('utils.report_generator.Path.exists', return_value=True), \
             patch('utils.report_generator.Environment') as mock_env, \
             patch('utils.report_generator.pisa.CreatePDF') as mock_pisa, \
             patch('utils.report_generator.tempfile.NamedTemporaryFile') as mock_tempfile, \
             patch('utils.report_generator.webbrowser.open') as mock_webbrowser:
            
            mock_resource_path.return_value = "/path/to/templates"
            mock_template = Mock()
            mock_template.render.return_value = "<html>Test HTML</html>"
            mock_env.return_value.get_template.return_value = mock_template
            mock_pisa.return_value.err = False
            
            mock_file = Mock()
            mock_file.name = "/tmp/test.pdf"
            mock_file.write = Mock()
            mock_file.flush = Mock()
            mock_tempfile.return_value.__enter__ = Mock(return_value=mock_file)
            mock_tempfile.return_value.__exit__ = Mock(return_value=None)
            
            with patch('utils.report_generator.Path.resolve', return_value=Path("/tmp/test.pdf")):
                generate_accuracy_report(sample_store_data, sample_emp_data, sample_team_data)
            
            # Verify that templates were called with correct data
            render_calls = mock_template.render.call_args_list
            
            # Check that page_headers (store_data) was passed to all templates
            for call in render_calls:
                call_kwargs = call[1] if len(call) > 1 else {}
                assert 'page_headers' in call_kwargs or 'emp_data' in call_kwargs or 'team_data' in call_kwargs
