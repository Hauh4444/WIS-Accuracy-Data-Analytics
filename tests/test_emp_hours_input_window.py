"""Tests for employee hours input window."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6 import QtWidgets, QtCore
import os

from views.emp_hours_input_window import EmpHoursInputWindow

pytestmark = pytest.mark.gui


class TestEmpHoursInputWindow:
    """Test EmpHoursInputWindow class."""
    
    def test_initialization(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test window initialization with data."""
        with patch('views.emp_hours_input_window.uic.loadUi') as mock_load_ui, \
             patch('views.emp_hours_input_window.resource_path') as mock_resource_path:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            window = EmpHoursInputWindow(sample_store_data, sample_emp_data, sample_team_data)
            
            assert window.store_data == sample_store_data
            assert window.emp_data == sample_emp_data
            assert window.team_data == sample_team_data
            assert len(window.rows_widgets) == len(sample_emp_data)
    
    def test_create_employee_row(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test employee row creation."""
        with patch('views.emp_hours_input_window.uic.loadUi') as mock_load_ui, \
             patch('views.emp_hours_input_window.resource_path') as mock_resource_path:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            window = EmpHoursInputWindow(sample_store_data, sample_emp_data, sample_team_data)
            
            emp = sample_emp_data[0]
            row = window.create_employee_row(emp)
            
            assert hasattr(row, 'txt_hours')
            assert hasattr(row, 'label_id')
            assert hasattr(row, 'label_name')
            assert row.txt_hours.text() == str(emp.get("hours", ""))
    
    def test_apply_emp_hour_input_row_style(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test employee row styling."""
        with patch('views.emp_hours_input_window.uic.loadUi') as mock_load_ui, \
             patch('views.emp_hours_input_window.resource_path') as mock_resource_path, \
             patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open_with_content("QWidget { background-color: white; }")):
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            window = EmpHoursInputWindow(sample_store_data, sample_emp_data, sample_team_data)
            
            emp = sample_emp_data[0]
            row = window.create_employee_row(emp)
            
            # Should not raise any exceptions
            window.apply_emp_hour_input_row_style(row)
    
    def test_apply_emp_hour_input_row_style_file_not_found(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test employee row styling when file doesn't exist."""
        with patch('views.emp_hours_input_window.uic.loadUi') as mock_load_ui, \
             patch('views.emp_hours_input_window.resource_path') as mock_resource_path, \
             patch('os.path.exists', return_value=False), \
             patch('builtins.print') as mock_print:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            window = EmpHoursInputWindow(sample_store_data, sample_emp_data, sample_team_data)
            
            emp = sample_emp_data[0]
            row = window.create_employee_row(emp)
            
            window.apply_emp_hour_input_row_style(row)
            mock_print.assert_called()
    
    def test_apply_scrollbar_style(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test scrollbar styling."""
        with patch('views.emp_hours_input_window.uic.loadUi') as mock_load_ui, \
             patch('views.emp_hours_input_window.resource_path') as mock_resource_path, \
             patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open_with_content("QScrollArea { background-color: white; }")):
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            window = EmpHoursInputWindow(sample_store_data, sample_emp_data, sample_team_data)
            
            # Should not raise any exceptions
            window.apply_scrollbar_style()
    
    def test_apply_scrollbar_style_file_not_found(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test scrollbar styling when file doesn't exist."""
        with patch('views.emp_hours_input_window.uic.loadUi') as mock_load_ui, \
             patch('views.emp_hours_input_window.resource_path') as mock_resource_path, \
             patch('os.path.exists', return_value=False), \
             patch('builtins.print') as mock_print:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            window = EmpHoursInputWindow(sample_store_data, sample_emp_data, sample_team_data)
            
            window.apply_scrollbar_style()
            mock_print.assert_called()
    
    def test_center_on_screen(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test window centering on screen."""
        with patch('views.emp_hours_input_window.uic.loadUi') as mock_load_ui, \
             patch('views.emp_hours_input_window.resource_path') as mock_resource_path, \
             patch('views.emp_hours_input_window.QtWidgets.QApplication.primaryScreen') as mock_screen:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_screen_instance = Mock()
            mock_screen_instance.availableGeometry.return_value = Mock()
            mock_screen_instance.availableGeometry.return_value.width.return_value = 1920
            mock_screen_instance.availableGeometry.return_value.height.return_value = 1080
            mock_screen.return_value = mock_screen_instance
            
            window = EmpHoursInputWindow(sample_store_data, sample_emp_data, sample_team_data)
            window.width.return_value = 800
            window.height.return_value = 600
            
            window.center_on_screen()
            
            mock_screen.assert_called_once()
    
    def test_center_on_screen_no_screen(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test window centering when no screen is available."""
        with patch('views.emp_hours_input_window.uic.loadUi') as mock_load_ui, \
             patch('views.emp_hours_input_window.resource_path') as mock_resource_path, \
             patch('views.emp_hours_input_window.QtWidgets.QApplication.primaryScreen', return_value=None):
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            window = EmpHoursInputWindow(sample_store_data, sample_emp_data, sample_team_data)
            
            # Should not raise any exceptions
            window.center_on_screen()
    
    def test_on_print_clicked_success(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test print button click with successful report generation."""
        with patch('views.emp_hours_input_window.uic.loadUi') as mock_load_ui, \
             patch('views.emp_hours_input_window.resource_path') as mock_resource_path, \
             patch('views.emp_hours_input_window.generate_accuracy_report') as mock_generate_report:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            window = EmpHoursInputWindow(sample_store_data, sample_emp_data, sample_team_data)
            
            # Mock the row widgets
            mock_row = Mock()
            mock_row.txt_hours.text.return_value = "8.0"
            window.rows_widgets = [mock_row]
            
            window.on_print_clicked()
            
            mock_generate_report.assert_called_once_with(
                store_data=sample_store_data,
                emp_data=sample_emp_data,
                team_data=sample_team_data
            )
    
    def test_on_print_clicked_no_data(self, sample_store_data, sample_team_data):
        """Test print button click with no employee data."""
        with patch('views.emp_hours_input_window.uic.loadUi') as mock_load_ui, \
             patch('views.emp_hours_input_window.resource_path') as mock_resource_path, \
             patch('views.emp_hours_input_window.QtWidgets.QMessageBox.warning') as mock_warning:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            window = EmpHoursInputWindow(sample_store_data, [], sample_team_data)
            window.rows_widgets = []
            
            window.on_print_clicked()
            
            mock_warning.assert_called_once()
    
    def test_on_print_clicked_hours_processing(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test hours processing in print button click."""
        with patch('views.emp_hours_input_window.uic.loadUi') as mock_load_ui, \
             patch('views.emp_hours_input_window.resource_path') as mock_resource_path, \
             patch('views.emp_hours_input_window.generate_accuracy_report') as mock_generate_report:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            window = EmpHoursInputWindow(sample_store_data, sample_emp_data, sample_team_data)
            
            # Mock the row widgets
            mock_row = Mock()
            mock_row.txt_hours.text.return_value = "8.0"
            window.rows_widgets = [mock_row]
            
            window.on_print_clicked()
            
            # Check that hours and UPH are calculated
            assert window.emp_data[0]["hours"] == 8.0
            assert window.emp_data[0]["uph"] == window.emp_data[0]["total_quantity"] / 8.0
    
    def test_on_print_clicked_invalid_hours(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test print button click with invalid hours input."""
        with patch('views.emp_hours_input_window.uic.loadUi') as mock_load_ui, \
             patch('views.emp_hours_input_window.resource_path') as mock_resource_path, \
             patch('views.emp_hours_input_window.generate_accuracy_report') as mock_generate_report:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            window = EmpHoursInputWindow(sample_store_data, sample_emp_data, sample_team_data)
            
            # Mock the row widgets with invalid hours
            mock_row = Mock()
            mock_row.txt_hours.text.return_value = "invalid"
            window.rows_widgets = [mock_row]
            
            window.on_print_clicked()
            
            # Check that invalid hours are handled
            assert window.emp_data[0]["hours"] == 0.0
            assert window.emp_data[0]["uph"] == 0.0
    
    def test_on_print_clicked_zero_hours(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test print button click with zero hours."""
        with patch('views.emp_hours_input_window.uic.loadUi') as mock_load_ui, \
             patch('views.emp_hours_input_window.resource_path') as mock_resource_path, \
             patch('views.emp_hours_input_window.generate_accuracy_report') as mock_generate_report:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            window = EmpHoursInputWindow(sample_store_data, sample_emp_data, sample_team_data)
            
            # Mock the row widgets with zero hours
            mock_row = Mock()
            mock_row.txt_hours.text.return_value = "0"
            window.rows_widgets = [mock_row]
            
            window.on_print_clicked()
            
            # Check that zero hours are handled
            assert window.emp_data[0]["hours"] == 0.0
            assert window.emp_data[0]["uph"] == 0.0


def mock_open_with_content(content):
    """Helper function to mock open with content."""
    def mock_open_func(path, mode='r'):
        mock_file = Mock()
        mock_file.read.return_value = content
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        return mock_file
    return mock_open_func
