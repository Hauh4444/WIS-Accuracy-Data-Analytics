import sys
import pytest
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from views.load_data_manual_dialog import LoadDataManualDialog


@pytest.fixture(scope="session")
def app():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    return app


class TestLoadDataManualDialog:

    def test_center_on_screen_functionality(self, app):
        """Test center on screen functionality."""
        dialog = LoadDataManualDialog()
        mock_screen = MagicMock()
        mock_screen.availableGeometry.return_value.width.return_value = 1920
        mock_screen.availableGeometry.return_value.height.return_value = 1080

        with patch.object(QtWidgets.QApplication, 'primaryScreen', return_value=mock_screen):
            dialog.center_on_screen()
            assert dialog.pos() is not None

    @patch("views.load_data_manual_dialog.QtWidgets.QFileDialog.getOpenFileName")
    def test_browse_database_sets_text(self, mock_file_dialog, app):
        """Test browse database sets text."""
        mock_file_dialog.return_value = ("/path/to/database.accdb", "")
        
        dialog = LoadDataManualDialog()
        dialog.browse_database()
        
        assert dialog.txtDatabasePath.text() == "/path/to/database.accdb"

    @patch("views.load_data_manual_dialog.QtWidgets.QFileDialog.getOpenFileName")
    def test_browse_database_cancelled(self, mock_file_dialog, app):
        """Test browse database when cancelled."""
        mock_file_dialog.return_value = ("", "")
        
        dialog = LoadDataManualDialog()
        dialog.browse_database()
        
        assert dialog.txtDatabasePath.text() == ""

    @patch("views.load_data_manual_dialog.get_db_connection")
    @patch("views.load_data_manual_dialog.load_store_data")
    @patch("views.load_data_manual_dialog.load_emp_data")
    @patch("views.load_data_manual_dialog.load_team_data")
    def test_load_database_success(self, mock_load_team, mock_load_emp, mock_load_store, mock_get_conn, app):
        """Test successful database loading."""
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_load_store.return_value = {"store": "Test Store"}
        mock_load_emp.return_value = [{"employee": "Test Emp"}]
        mock_load_team.return_value = [{"team": "Test Team"}]
        
        dialog = LoadDataManualDialog()
        dialog.txtDatabasePath.setText("/path/to/database.accdb")
        
        dialog.load_database()
        
        assert dialog.store_data == {"store": "Test Store"}
        assert dialog.emp_data == [{"employee": "Test Emp"}]
        assert dialog.team_data == [{"team": "Test Team"}]
        mock_conn.close.assert_called_once()

    @patch("views.load_data_manual_dialog.get_db_connection")
    def test_load_database_no_connection(self, mock_get_conn, app):
        """Test no connection handling."""
        mock_get_conn.return_value = None
        
        dialog = LoadDataManualDialog()
        dialog.txtDatabasePath.setText("/path/to/database.accdb")
        
        dialog.load_database()
        
        assert not hasattr(dialog, 'store_data')

    @patch("views.load_data_manual_dialog.QtWidgets.QMessageBox.warning")
    def test_empty_database_path(self, mock_warning, app):
        """Test empty database path shows warning."""
        dialog = LoadDataManualDialog()
        dialog.txtDatabasePath.setText("")
        
        dialog.load_database()
        
        mock_warning.assert_called_once()

    @patch("views.load_data_manual_dialog.QtWidgets.QMessageBox.warning")
    def test_whitespace_database_path(self, mock_warning, app):
        """Test whitespace database path shows warning."""
        dialog = LoadDataManualDialog()
        dialog.txtDatabasePath.setText("   ")
        
        dialog.load_database()
        
        mock_warning.assert_called_once()