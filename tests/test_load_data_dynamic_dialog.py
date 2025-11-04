"""Tests for dynamic data loading dialog."""
import pytest
from unittest.mock import Mock, patch
from PyQt6 import QtWidgets

from views.load_data_dynamic_dialog import LoadDataDynamicDialog

pytestmark = pytest.mark.gui


class TestLoadDataDynamicDialog:
    """Test LoadDataDynamicDialog class."""
    
    def test_initialization(self):
        """Test dialog initialization."""
        with patch('views.load_data_dynamic_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_dynamic_dialog.resource_path') as mock_resource_path:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            dialog = LoadDataDynamicDialog()
            
            assert hasattr(dialog, 'btnLoad')
            assert hasattr(dialog, 'txtJobNumber')
    
    def test_center_on_screen(self):
        """Test dialog centering on screen."""
        with patch('views.load_data_dynamic_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_dynamic_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_dynamic_dialog.QtWidgets.QApplication.primaryScreen') as mock_screen:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_screen_instance = Mock()
            mock_screen_instance.availableGeometry.return_value = Mock()
            mock_screen_instance.availableGeometry.return_value.width.return_value = 1920
            mock_screen_instance.availableGeometry.return_value.height.return_value = 1080
            mock_screen.return_value = mock_screen_instance
            
            dialog = LoadDataDynamicDialog()
            dialog.width.return_value = 400
            dialog.height.return_value = 300
            
            dialog.center_on_screen()
            
            mock_screen.assert_called_once()
    
    def test_center_on_screen_no_screen(self):
        """Test dialog centering when no screen is available."""
        with patch('views.load_data_dynamic_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_dynamic_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_dynamic_dialog.QtWidgets.QApplication.primaryScreen', return_value=None):
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            dialog = LoadDataDynamicDialog()
            
            # Should not raise any exceptions
            dialog.center_on_screen()
    
    def test_load_database_empty_job_number(self):
        """Test database loading with empty job number."""
        with patch('views.load_data_dynamic_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_dynamic_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_dynamic_dialog.QtWidgets.QMessageBox.warning') as mock_warning:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            dialog = LoadDataDynamicDialog()
            dialog.txtJobNumber = Mock()
            dialog.txtJobNumber.text.return_value = ""
            
            dialog.load_database()
            
            mock_warning.assert_called_once_with(dialog, "Input Required", "Please enter a Job Number.")
    
    def test_load_database_whitespace_job_number(self):
        """Test database loading with whitespace-only job number."""
        with patch('views.load_data_dynamic_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_dynamic_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_dynamic_dialog.QtWidgets.QMessageBox.warning') as mock_warning:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            dialog = LoadDataDynamicDialog()
            dialog.txtJobNumber = Mock()
            dialog.txtJobNumber.text.return_value = "   "
            
            dialog.load_database()
            
            mock_warning.assert_called_once_with(dialog, "Input Required", "Please enter a Job Number.")
    
    def test_load_database_connection_failed(self):
        """Test database loading when connection fails."""
        with patch('views.load_data_dynamic_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_dynamic_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_dynamic_dialog.get_db_connection') as mock_get_connection:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_get_connection.return_value = None
            
            dialog = LoadDataDynamicDialog()
            dialog.txtJobNumber = Mock()
            dialog.txtJobNumber.text.return_value = "12345"
            dialog.reject = Mock()
            
            dialog.load_database()
            
            expected_path = r"C:\WISDOM\JOBS\12345\11355\12345.MDB"
            mock_get_connection.assert_called_once_with(db_path=expected_path)
            dialog.reject.assert_called_once()
    
    def test_load_database_success(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test successful database loading."""
        with patch('views.load_data_dynamic_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_dynamic_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_dynamic_dialog.get_db_connection') as mock_get_connection, \
             patch('views.load_data_dynamic_dialog.load_store_data') as mock_load_store, \
             patch('views.load_data_dynamic_dialog.load_emp_data') as mock_load_emp, \
             patch('views.load_data_dynamic_dialog.load_team_data') as mock_load_team:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_conn = Mock()
            mock_get_connection.return_value = mock_conn
            mock_load_store.return_value = sample_store_data
            mock_load_emp.return_value = sample_emp_data
            mock_load_team.return_value = sample_team_data
            
            dialog = LoadDataDynamicDialog()
            dialog.txtJobNumber = Mock()
            dialog.txtJobNumber.text.return_value = "12345"
            dialog.accept = Mock()
            
            dialog.load_database()
            
            expected_path = r"C:\WISDOM\JOBS\12345\11355\12345.MDB"
            mock_get_connection.assert_called_once_with(db_path=expected_path)
            mock_load_store.assert_called_once_with(conn=mock_conn)
            mock_load_emp.assert_called_once_with(conn=mock_conn)
            mock_load_team.assert_called_once_with(conn=mock_conn)
            dialog.accept.assert_called_once()
            mock_conn.close.assert_called_once()
    
    def test_load_database_exception(self):
        """Test database loading with exception."""
        with patch('views.load_data_dynamic_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_dynamic_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_dynamic_dialog.get_db_connection') as mock_get_connection, \
             patch('views.load_data_dynamic_dialog.traceback.print_exc') as mock_traceback:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_conn = Mock()
            mock_get_connection.return_value = mock_conn
            mock_load_store = Mock(side_effect=Exception("Database error"))
            
            with patch('views.load_data_dynamic_dialog.load_store_data', mock_load_store):
                dialog = LoadDataDynamicDialog()
                dialog.txtJobNumber = Mock()
                dialog.txtJobNumber.text.return_value = "12345"
                dialog.reject = Mock()
                
                dialog.load_database()
                
                mock_traceback.assert_called_once()
                dialog.reject.assert_called_once()
                mock_conn.close.assert_called_once()
    
    def test_load_database_connection_close_on_exception(self):
        """Test that connection is closed even when exception occurs."""
        with patch('views.load_data_dynamic_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_dynamic_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_dynamic_dialog.get_db_connection') as mock_get_connection, \
             patch('views.load_data_dynamic_dialog.traceback.print_exc') as mock_traceback:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_conn = Mock()
            mock_get_connection.return_value = mock_conn
            
            with patch('views.load_data_dynamic_dialog.load_store_data', side_effect=Exception("Database error")):
                dialog = LoadDataDynamicDialog()
                dialog.txtJobNumber = Mock()
                dialog.txtJobNumber.text.return_value = "12345"
                dialog.reject = Mock()
                
                dialog.load_database()
                
                mock_conn.close.assert_called_once()
    
    def test_load_database_none_connection_close(self):
        """Test that None connection doesn't cause error in finally block."""
        with patch('views.load_data_dynamic_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_dynamic_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_dynamic_dialog.get_db_connection') as mock_get_connection, \
             patch('views.load_data_dynamic_dialog.traceback.print_exc') as mock_traceback:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_get_connection.return_value = None
            
            dialog = LoadDataDynamicDialog()
            dialog.txtJobNumber = Mock()
            dialog.txtJobNumber.text.return_value = "12345"
            dialog.reject = Mock()
            
            # Should not raise any exceptions
            dialog.load_database()
    
    def test_wisdom_path_convention(self):
        """Test that WISDOM path convention is followed."""
        with patch('views.load_data_dynamic_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_dynamic_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_dynamic_dialog.get_db_connection') as mock_get_connection:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_get_connection.return_value = None
            
            dialog = LoadDataDynamicDialog()
            dialog.txtJobNumber = Mock()
            dialog.txtJobNumber.text.return_value = "67890"
            dialog.reject = Mock()
            
            dialog.load_database()
            
            expected_path = r"C:\WISDOM\JOBS\67890\11355\67890.MDB"
            mock_get_connection.assert_called_once_with(db_path=expected_path)
    
    def test_job_number_stripping(self):
        """Test that job number is properly stripped."""
        with patch('views.load_data_dynamic_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_dynamic_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_dynamic_dialog.get_db_connection') as mock_get_connection:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_get_connection.return_value = None
            
            dialog = LoadDataDynamicDialog()
            dialog.txtJobNumber = Mock()
            dialog.txtJobNumber.text.return_value = "  12345  "  # With whitespace
            dialog.reject = Mock()
            
            dialog.load_database()
            
            expected_path = r"C:\WISDOM\JOBS\12345\11355\12345.MDB"
            mock_get_connection.assert_called_once_with(db_path=expected_path)
