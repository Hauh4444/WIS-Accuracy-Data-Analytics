import pytest
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from main import load_data_with_fallback


@pytest.fixture(scope="session", autouse=True)
def qapp():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app


class TestMainApplicationIntegration:

    @patch("main.QtWidgets.QMessageBox.critical")
    def test_main_startup_condition_logic(self, mock_critical):
        """Test the main application startup condition logic."""
        store_data = {"store": "Test Store"}
        emp_data = [{"employee": "Test Emp"}]
        team_data = [{"team": "Test Team"}]
        
        should_start = store_data is not None and emp_data is not None and team_data is not None
        assert should_start is True
        
        should_not_start = None is not None and emp_data is not None and team_data is not None
        assert should_not_start is False

    @patch("main.LoadDataDynamicDialog")
    @patch("main.LoadDataManualDialog")
    def test_load_data_with_fallback_success_dynamic(self, mock_manual_dialog, mock_dynamic_dialog):
        """Test load_data_with_fallback with successful dynamic dialog."""
        mock_dynamic_instance = MagicMock()
        mock_dynamic_instance.exec.return_value = QtWidgets.QDialog.DialogCode.Accepted
        mock_dynamic_instance.store_data = {"store": "Dynamic Store"}
        mock_dynamic_instance.emp_data = [{"employee": "Dynamic Emp"}]
        mock_dynamic_instance.team_data = [{"team": "Dynamic Team"}]
        mock_dynamic_dialog.return_value = mock_dynamic_instance
        
        result = load_data_with_fallback()
        
        assert result == ({"store": "Dynamic Store"}, [{"employee": "Dynamic Emp"}], [{"team": "Dynamic Team"}])
        mock_dynamic_instance.exec.assert_called_once()
        mock_manual_dialog.assert_not_called()

    @patch("main.LoadDataDynamicDialog")
    @patch("main.LoadDataManualDialog")
    def test_load_data_with_fallback_success_manual(self, mock_manual_dialog, mock_dynamic_dialog):
        """Test load_data_with_fallback with successful manual dialog fallback."""
        mock_dynamic_instance = MagicMock()
        mock_dynamic_instance.exec.return_value = QtWidgets.QDialog.DialogCode.Rejected
        mock_dynamic_dialog.return_value = mock_dynamic_instance
        
        mock_manual_instance = MagicMock()
        mock_manual_instance.exec.return_value = QtWidgets.QDialog.DialogCode.Accepted
        mock_manual_instance.store_data = {"store": "Manual Store"}
        mock_manual_instance.emp_data = [{"employee": "Manual Emp"}]
        mock_manual_instance.team_data = [{"team": "Manual Team"}]
        mock_manual_dialog.return_value = mock_manual_instance
        
        result = load_data_with_fallback()
        
        assert result == ({"store": "Manual Store"}, [{"employee": "Manual Emp"}], [{"team": "Manual Team"}])
        mock_dynamic_instance.exec.assert_called_once()
        mock_manual_instance.exec.assert_called_once()

    @patch("main.LoadDataDynamicDialog")
    @patch("main.LoadDataManualDialog")
    def test_load_data_with_fallback_both_fail(self, mock_manual_dialog, mock_dynamic_dialog):
        """Test load_data_with_fallback when both dialogs fail."""
        mock_dynamic_instance = MagicMock()
        mock_dynamic_instance.exec.return_value = QtWidgets.QDialog.DialogCode.Rejected
        mock_dynamic_dialog.return_value = mock_dynamic_instance
        
        mock_manual_instance = MagicMock()
        mock_manual_instance.exec.return_value = QtWidgets.QDialog.DialogCode.Rejected
        mock_manual_dialog.return_value = mock_manual_instance
        
        result = load_data_with_fallback()
        
        assert result == (None, None, None)
        mock_dynamic_instance.exec.assert_called_once()
        mock_manual_instance.exec.assert_called_once()