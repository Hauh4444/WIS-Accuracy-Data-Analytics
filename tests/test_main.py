"""Tests for main application entry point."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6 import QtWidgets

from main import load_data_with_fallback


class TestLoadDataWithFallback:
    """Test load_data_with_fallback function."""
    
    def test_dynamic_dialog_accepted(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test successful data loading with dynamic dialog."""
        with patch('main.LoadDataDynamicDialog') as mock_dynamic_dialog_class, \
             patch('main.LoadDataManualDialog') as mock_manual_dialog_class:
            
            # Mock dynamic dialog success
            mock_dynamic_dialog = Mock()
            mock_dynamic_dialog.exec.return_value = QtWidgets.QDialog.DialogCode.Accepted
            mock_dynamic_dialog.store_data = sample_store_data
            mock_dynamic_dialog.emp_data = sample_emp_data
            mock_dynamic_dialog.team_data = sample_team_data
            mock_dynamic_dialog_class.return_value = mock_dynamic_dialog
            
            result = load_data_with_fallback()
            
            assert result == (sample_store_data, sample_emp_data, sample_team_data)
            mock_dynamic_dialog_class.assert_called_once()
            mock_manual_dialog_class.assert_not_called()
    
    def test_dynamic_dialog_rejected_manual_accepted(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test fallback to manual dialog when dynamic dialog is rejected."""
        with patch('main.LoadDataDynamicDialog') as mock_dynamic_dialog_class, \
             patch('main.LoadDataManualDialog') as mock_manual_dialog_class:
            
            # Mock dynamic dialog rejection
            mock_dynamic_dialog = Mock()
            mock_dynamic_dialog.exec.return_value = QtWidgets.QDialog.DialogCode.Rejected
            mock_dynamic_dialog_class.return_value = mock_dynamic_dialog
            
            # Mock manual dialog success
            mock_manual_dialog = Mock()
            mock_manual_dialog.exec.return_value = QtWidgets.QDialog.DialogCode.Accepted
            mock_manual_dialog.store_data = sample_store_data
            mock_manual_dialog.emp_data = sample_emp_data
            mock_manual_dialog.team_data = sample_team_data
            mock_manual_dialog_class.return_value = mock_manual_dialog
            
            result = load_data_with_fallback()
            
            assert result == (sample_store_data, sample_emp_data, sample_team_data)
            mock_dynamic_dialog_class.assert_called_once()
            mock_manual_dialog_class.assert_called_once()
    
    def test_both_dialogs_rejected(self):
        """Test when both dialogs are rejected."""
        with patch('main.LoadDataDynamicDialog') as mock_dynamic_dialog_class, \
             patch('main.LoadDataManualDialog') as mock_manual_dialog_class:
            
            # Mock both dialogs rejection
            mock_dynamic_dialog = Mock()
            mock_dynamic_dialog.exec.return_value = QtWidgets.QDialog.DialogCode.Rejected
            mock_dynamic_dialog_class.return_value = mock_dynamic_dialog
            
            mock_manual_dialog = Mock()
            mock_manual_dialog.exec.return_value = QtWidgets.QDialog.DialogCode.Rejected
            mock_manual_dialog_class.return_value = mock_manual_dialog
            
            result = load_data_with_fallback()
            
            assert result == (None, None, None)
            mock_dynamic_dialog_class.assert_called_once()
            mock_manual_dialog_class.assert_called_once()
    
    def test_dynamic_dialog_missing_attributes(self):
        """Test when dynamic dialog doesn't have required attributes."""
        with patch('main.LoadDataDynamicDialog') as mock_dynamic_dialog_class, \
             patch('main.LoadDataManualDialog') as mock_manual_dialog_class:
            
            # Mock dynamic dialog with missing attributes
            mock_dynamic_dialog = Mock()
            mock_dynamic_dialog.exec.return_value = QtWidgets.QDialog.DialogCode.Accepted
            # Missing store_data, emp_data, team_data attributes
            mock_dynamic_dialog_class.return_value = mock_dynamic_dialog
            
            # Mock manual dialog success
            mock_manual_dialog = Mock()
            mock_manual_dialog.exec.return_value = QtWidgets.QDialog.DialogCode.Accepted
            mock_manual_dialog.store_data = {"store": "Test Store"}
            mock_manual_dialog.emp_data = []
            mock_manual_dialog.team_data = []
            mock_manual_dialog_class.return_value = mock_manual_dialog
            
            result = load_data_with_fallback()
            
            assert result == ({"store": "Test Store"}, [], [])
            mock_dynamic_dialog_class.assert_called_once()
            mock_manual_dialog_class.assert_called_once()
    
    def test_manual_dialog_missing_attributes(self):
        """Test when manual dialog doesn't have required attributes."""
        with patch('main.LoadDataDynamicDialog') as mock_dynamic_dialog_class, \
             patch('main.LoadDataManualDialog') as mock_manual_dialog_class:
            
            # Mock dynamic dialog rejection
            mock_dynamic_dialog = Mock()
            mock_dynamic_dialog.exec.return_value = QtWidgets.QDialog.DialogCode.Rejected
            mock_dynamic_dialog_class.return_value = mock_dynamic_dialog
            
            # Mock manual dialog with missing attributes
            mock_manual_dialog = Mock()
            mock_manual_dialog.exec.return_value = QtWidgets.QDialog.DialogCode.Accepted
            # Missing store_data, emp_data, team_data attributes
            mock_manual_dialog_class.return_value = mock_manual_dialog
            
            result = load_data_with_fallback()
            
            assert result == (None, None, None)
            mock_dynamic_dialog_class.assert_called_once()
            mock_manual_dialog_class.assert_called_once()
    
    def test_dynamic_dialog_partial_attributes(self):
        """Test when dynamic dialog has some but not all required attributes."""
        with patch('main.LoadDataDynamicDialog') as mock_dynamic_dialog_class, \
             patch('main.LoadDataManualDialog') as mock_manual_dialog_class:
            
            # Mock dynamic dialog with partial attributes
            mock_dynamic_dialog = Mock()
            mock_dynamic_dialog.exec.return_value = QtWidgets.QDialog.DialogCode.Accepted
            mock_dynamic_dialog.store_data = {"store": "Test Store"}
            # Missing emp_data and team_data
            mock_dynamic_dialog_class.return_value = mock_dynamic_dialog
            
            # Mock manual dialog success
            mock_manual_dialog = Mock()
            mock_manual_dialog.exec.return_value = QtWidgets.QDialog.DialogCode.Accepted
            mock_manual_dialog.store_data = {"store": "Test Store"}
            mock_manual_dialog.emp_data = []
            mock_manual_dialog.team_data = []
            mock_manual_dialog_class.return_value = mock_manual_dialog
            
            result = load_data_with_fallback()
            
            assert result == ({"store": "Test Store"}, [], [])
            mock_dynamic_dialog_class.assert_called_once()
            mock_manual_dialog_class.assert_called_once()


class TestMainApplication:
    """Test main application execution."""
    
    def test_main_success(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test successful main application execution."""
        with patch('main.QtWidgets.QApplication') as mock_app_class, \
             patch('main.load_data_with_fallback') as mock_load_data, \
             patch('main.EmpHoursInputWindow') as mock_window_class, \
             patch('main.QtWidgets.QMessageBox.critical') as mock_msgbox:
            
            # Mock application
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            
            # Mock data loading
            mock_load_data.return_value = (sample_store_data, sample_emp_data, sample_team_data)
            
            # Mock window
            mock_window = Mock()
            mock_window_class.return_value = mock_window
            
            # Import and run main
            import main
            main.main()
            
            mock_app_class.assert_called_once()
            mock_load_data.assert_called_once()
            mock_window_class.assert_called_once_with(
                store_data=sample_store_data,
                emp_data=sample_emp_data,
                team_data=sample_team_data
            )
            mock_window.setWindowTitle.assert_called_once_with("WIS Accuracy Data Analytics")
            mock_window.show.assert_called_once()
            mock_window.raise_.assert_called_once()
            mock_window.activateWindow.assert_called_once()
            mock_app.exec.assert_called_once()
    
    def test_main_no_data(self):
        """Test main application when no data is loaded."""
        with patch('main.QtWidgets.QApplication') as mock_app_class, \
             patch('main.load_data_with_fallback') as mock_load_data, \
             patch('main.EmpHoursInputWindow') as mock_window_class, \
             patch('main.QtWidgets.QMessageBox.critical') as mock_msgbox:
            
            # Mock application
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            
            # Mock no data loading
            mock_load_data.return_value = (None, None, None)
            
            # Import and run main
            import main
            main.main()
            
            mock_app_class.assert_called_once()
            mock_load_data.assert_called_once()
            mock_window_class.assert_not_called()
            mock_app.exec.assert_called_once()
    
    def test_main_partial_data(self):
        """Test main application when only partial data is loaded."""
        with patch('main.QtWidgets.QApplication') as mock_app_class, \
             patch('main.load_data_with_fallback') as mock_load_data, \
             patch('main.EmpHoursInputWindow') as mock_window_class, \
             patch('main.QtWidgets.QMessageBox.critical') as mock_msgbox:
            
            # Mock application
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            
            # Mock partial data loading
            mock_load_data.return_value = ({"store": "Test"}, None, None)
            
            # Import and run main
            import main
            main.main()
            
            mock_app_class.assert_called_once()
            mock_load_data.assert_called_once()
            mock_window_class.assert_not_called()
            mock_app.exec.assert_called_once()
    
    def test_main_exception_handling(self):
        """Test main application exception handling."""
        with patch('main.QtWidgets.QApplication') as mock_app_class, \
             patch('main.load_data_with_fallback', side_effect=Exception("Test error")), \
             patch('main.QtWidgets.QMessageBox.critical') as mock_msgbox:
            
            # Mock application
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            
            # Import and run main
            import main
            main.main()
            
            mock_app_class.assert_called_once()
            mock_msgbox.assert_called_once_with(
                None,
                "Application Error",
                "An unexpected error occurred:\nTest error"
            )
            mock_app.exec.assert_called_once()
    
    def test_main_window_creation_failure(self, sample_store_data, sample_emp_data, sample_team_data):
        """Test main application when window creation fails."""
        with patch('main.QtWidgets.QApplication') as mock_app_class, \
             patch('main.load_data_with_fallback') as mock_load_data, \
             patch('main.EmpHoursInputWindow', side_effect=Exception("Window creation error")), \
             patch('main.QtWidgets.QMessageBox.critical') as mock_msgbox:
            
            # Mock application
            mock_app = Mock()
            mock_app_class.return_value = mock_app
            
            # Mock data loading
            mock_load_data.return_value = (sample_store_data, sample_emp_data, sample_team_data)
            
            # Import and run main
            import main
            main.main()
            
            mock_app_class.assert_called_once()
            mock_load_data.assert_called_once()
            mock_msgbox.assert_called_once_with(
                None,
                "Application Error",
                "An unexpected error occurred:\nWindow creation error"
            )
            mock_app.exec.assert_called_once()
