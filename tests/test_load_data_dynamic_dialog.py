import sys
import pytest
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from views.load_data_dynamic_dialog import LoadDataDynamicDialog


@pytest.fixture(scope="session")
def app():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    return app


class TestLoadDataDynamicDialog:

    def test_center_on_screen_functionality(self, app):
        """Test center on screen functionality."""
        dialog = LoadDataDynamicDialog()
        mock_screen = MagicMock()
        mock_screen.availableGeometry.return_value.width.return_value = 1920
        mock_screen.availableGeometry.return_value.height.return_value = 1080

        with patch.object(QtWidgets.QApplication, 'primaryScreen', return_value=mock_screen):
            dialog.center_on_screen()
            assert dialog.pos() is not None

    @patch("views.load_data_dynamic_dialog.get_db_connection")
    @patch("views.load_data_dynamic_dialog.load_store_data")
    @patch("views.load_data_dynamic_dialog.load_emp_data")
    @patch("views.load_data_dynamic_dialog.load_team_data")
    def test_load_database_success(self, mock_load_team, mock_load_emp, mock_load_store, mock_get_conn, app):
        """Test successful database loading."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_load_store.return_value = {"store": "Test Store"}
        mock_load_emp.return_value = [{"employee": "Test Emp"}]
        mock_load_team.return_value = [{"team": "Test Team"}]
        
        dialog = LoadDataDynamicDialog()
        dialog.txtJobNumber.setText("TEST123")
        
        dialog.load_database()
        
        assert dialog.store_data == {"store": "Test Store"}
        assert dialog.emp_data == [{"employee": "Test Emp"}]
        assert dialog.team_data == [{"team": "Test Team"}]
        mock_conn.close.assert_called_once()

    @patch("views.load_data_dynamic_dialog.QtWidgets.QMessageBox.warning")
    def test_load_database_empty_job_number_shows_warning(self, mock_warning, app):
        """Test empty job number shows warning."""
        dialog = LoadDataDynamicDialog()
        dialog.txtJobNumber.setText("")
        
        dialog.load_database()
        
        mock_warning.assert_called_once()

    @patch("views.load_data_dynamic_dialog.get_db_connection")
    def test_load_database_no_connection_rejects_dialog(self, mock_get_conn, app):
        """Test no connection rejects dialog."""
        mock_get_conn.return_value = None
        
        dialog = LoadDataDynamicDialog()
        dialog.txtJobNumber.setText("TEST123")
        
        dialog.load_database()
        
        assert not hasattr(dialog, 'store_data')

    @patch("views.load_data_dynamic_dialog.get_db_connection")
    @patch("views.load_data_dynamic_dialog.load_store_data")
    @patch("views.load_data_dynamic_dialog.load_emp_data")
    @patch("views.load_data_dynamic_dialog.load_team_data")
    def test_load_database_error_handling(self, mock_load_team, mock_load_emp, mock_load_store, mock_get_conn, app):
        """Test error handling during data loading."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_load_store.side_effect = Exception("Store data error")
        
        dialog = LoadDataDynamicDialog()
        dialog.txtJobNumber.setText("TEST123")
        
        dialog.load_database()
        
        assert not hasattr(dialog, 'store_data')
        mock_conn.close.assert_called_once()