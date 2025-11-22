"""Tests for manual data loading dialog."""
import pytest
from unittest.mock import Mock, patch
from PyQt6 import QtWidgets

from views import LoadDataManualDialog

pytestmark = pytest.mark.gui


class TestLoadDataManualDialog:
    """Test LoadDataManualDialog class."""
    
    def test_initialization(self):
        """Test dialog initialization."""
        with patch('views.load_data_manual_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_manual_dialog.resource_path') as mock_resource_path:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            dialog = LoadDataManualDialog()
            
            assert hasattr(dialog, 'btnBrowse')
            assert hasattr(dialog, 'btnLoad')
            assert hasattr(dialog, 'txtDatabasePath')
    
    def test_center_on_screen(self):
        """Test dialog centering on screen."""
        with patch('views.load_data_manual_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_manual_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_manual_dialog.QtWidgets.QApplication.primaryScreen') as mock_screen:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_screen_instance = Mock()
            mock_screen_instance.availableGeometry.return_value = Mock()
            mock_screen_instance.availableGeometry.return_value.width.return_value = 1920
            mock_screen_instance.availableGeometry.return_value.height.return_value = 1080
            mock_screen.return_value = mock_screen_instance
            
            dialog = LoadDataManualDialog()
            dialog.width.return_value = 400
            dialog.height.return_value = 300
            
            dialog.center_on_screen()
            
            mock_screen.assert_called_once()
    
    def test_center_on_screen_no_screen(self):
        """Test dialog centering when no screen is available."""
        with patch('views.load_data_manual_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_manual_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_manual_dialog.QtWidgets.QApplication.primaryScreen', return_value=None):
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_widget.layout.return_value = Mock()
            mock_load_ui.return_value = mock_widget
            
            dialog = LoadDataManualDialog()
            
            # Should not raise any exceptions
            dialog.center_on_screen()
    
    def test_browse_database_success(self):
        """Test successful database file browsing."""
        with patch('views.load_data_manual_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_manual_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_manual_dialog.QtWidgets.QFileDialog.getOpenFileName') as mock_file_dialog:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_file_dialog.return_value = ("/path/to/test.mdb", "Access Databases (*.mdb *.accdb)")
            
            dialog = LoadDataManualDialog()
            dialog.txtDatabasePath = Mock()
            
            dialog.browse_database()
            
            mock_file_dialog.assert_called_once_with(
                dialog,
                "Select Database File",
                "",
                "Access Databases (*.mdb *.accdb);;All Files (*)"
            )
            dialog.txtDatabasePath.setText.assert_called_once_with("/path/to/test.mdb")
    
    def test_browse_database_cancelled(self):
        """Test database file browsing when cancelled."""
        with patch('views.load_data_manual_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_manual_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_manual_dialog.QtWidgets.QFileDialog.getOpenFileName') as mock_file_dialog:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_file_dialog.return_value = ("", "")
            
            dialog = LoadDataManualDialog()
            dialog.txtDatabasePath = Mock()
            
            dialog.browse_database()
            
            dialog.txtDatabasePath.setText.assert_not_called()
    
    def test_load_database_empty_path(self):
        """Test database loading with empty path."""
        with patch('views.load_data_manual_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_manual_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_manual_dialog.QtWidgets.QMessageBox.warning') as mock_warning:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            dialog = LoadDataManualDialog()
            dialog.txtDatabasePath = Mock()
            dialog.txtDatabasePath.text.return_value = ""
            
            dialog.load_database()
            
            mock_warning.assert_called_once_with(dialog, "Input Required", "Please enter a Database Path.")
    
    def test_load_database_whitespace_path(self):
        """Test database loading with whitespace-only path."""
        with patch('views.load_data_manual_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_manual_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_manual_dialog.QtWidgets.QMessageBox.warning') as mock_warning:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            dialog = LoadDataManualDialog()
            dialog.txtDatabasePath = Mock()
            dialog.txtDatabasePath.text.return_value = "   "
            
            dialog.load_database()
            
            mock_warning.assert_called_once_with(dialog, "Input Required", "Please enter a Database Path.")
    
    def test_load_database_connection_failed(self):
        """Test database loading when connection fails."""
        with patch('views.load_data_manual_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_manual_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_manual_dialog.get_db_connection') as mock_get_connection:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_get_connection.return_value = None
            
            dialog = LoadDataManualDialog()
            dialog.txtDatabasePath = Mock()
            dialog.txtDatabasePath.text.return_value = "/path/to/test.mdb"
            
            dialog.load_database()
            
            mock_get_connection.assert_called_once_with(db_path="/path/to/test.mdb")
    
    def test_load_database_success(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test successful database loading."""
        with patch('views.load_data_manual_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_manual_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_manual_dialog.get_db_connection') as mock_get_connection, \
             patch('views.load_data_manual_dialog.load_store_data') as mock_load_store, \
             patch('views.load_data_manual_dialog.load_emp_data') as mock_load_emp, \
             patch('views.load_data_manual_dialog.load_team_data') as mock_load_team:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_conn = Mock()
            mock_get_connection.return_value = mock_conn
            mock_load_store.return_value = sample_store_data
            mock_load_emp.return_value = sample_emp_data
            mock_load_team.return_value = sample_team_data
            
            dialog = LoadDataManualDialog()
            dialog.txtDatabasePath = Mock()
            dialog.txtDatabasePath.text.return_value = "/path/to/test.mdb"
            dialog.accept = Mock()
            
            dialog.load_database()
            
            mock_get_connection.assert_called_once_with(db_path="/path/to/test.mdb")
            mock_load_store.assert_called_once_with(conn=mock_conn)
            mock_load_emp.assert_called_once_with(conn=mock_conn)
            mock_load_team.assert_called_once_with(conn=mock_conn)
            dialog.accept.assert_called_once()
            mock_conn.close.assert_called_once()
    
    def test_load_database_exception(self):
        """Test database loading with exception."""
        with patch('views.load_data_manual_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_manual_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_manual_dialog.get_db_connection') as mock_get_connection, \
             patch('views.load_data_manual_dialog.traceback.print_exc') as mock_traceback:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_conn = Mock()
            mock_get_connection.return_value = mock_conn
            mock_load_store = Mock(side_effect=Exception("Database error"))
            
            with patch('views.load_data_manual_dialog.load_store_data', mock_load_store):
                dialog = LoadDataManualDialog()
                dialog.txtDatabasePath = Mock()
                dialog.txtDatabasePath.text.return_value = "/path/to/test.mdb"
                
                dialog.load_database()
                
                mock_traceback.assert_called_once()
                mock_conn.close.assert_called_once()
    
    def test_load_database_connection_close_on_exception(self):
        """Test that connection is closed even when exception occurs."""
        with patch('views.load_data_manual_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_manual_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_manual_dialog.get_db_connection') as mock_get_connection, \
             patch('views.load_data_manual_dialog.traceback.print_exc') as mock_traceback:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_conn = Mock()
            mock_get_connection.return_value = mock_conn
            
            with patch('views.load_data_manual_dialog.load_store_data', side_effect=Exception("Database error")):
                dialog = LoadDataManualDialog()
                dialog.txtDatabasePath = Mock()
                dialog.txtDatabasePath.text.return_value = "/path/to/test.mdb"
                
                dialog.load_database()
                
                mock_conn.close.assert_called_once()
    
    def test_load_database_none_connection_close(self):
        """Test that None connection doesn't cause error in finally block."""
        with patch('views.load_data_manual_dialog.uic.loadUi') as mock_load_ui, \
             patch('views.load_data_manual_dialog.resource_path') as mock_resource_path, \
             patch('views.load_data_manual_dialog.get_db_connection') as mock_get_connection, \
             patch('views.load_data_manual_dialog.traceback.print_exc') as mock_traceback:
            
            mock_resource_path.return_value = "/path/to/ui"
            mock_widget = Mock()
            mock_load_ui.return_value = mock_widget
            
            mock_get_connection.return_value = None
            
            dialog = LoadDataManualDialog()
            dialog.txtDatabasePath = Mock()
            dialog.txtDatabasePath.text.return_value = "/path/to/test.mdb"
            
            # Should not raise any exceptions
            dialog.load_database()
