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

    def test_dialog_initialization(self, app):
        with patch("views.load_data_manual_dialog.resource_path") as mock_resource_path:
            mock_resource_path.return_value = "/fake/path/ui"
            
            def mock_load_ui(ui_path, dialog):
                dialog.btnBrowse = MagicMock()
                dialog.btnLoad = MagicMock()
                dialog.txtDatabasePath = MagicMock()
            
            with patch("views.load_data_manual_dialog.uic.loadUi", side_effect=mock_load_ui):
                dialog = LoadDataManualDialog()
                
                assert hasattr(dialog, 'btnBrowse')
                assert hasattr(dialog, 'btnLoad')
                assert hasattr(dialog, 'txtDatabasePath')

    def test_center_on_screen_moves_dialog(self, app):
        dialog = LoadDataManualDialog()

        mock_screen = MagicMock()
        mock_screen.availableGeometry.return_value.width.return_value = 1920
        mock_screen.availableGeometry.return_value.height.return_value = 1080

        with patch.object(QtWidgets.QApplication, 'primaryScreen', return_value=mock_screen):
            dialog.center_on_screen()
            assert dialog.pos() is not None

    def test_center_on_screen_no_screen(self, app):
        dialog = LoadDataManualDialog()

        with patch.object(QtWidgets.QApplication, 'primaryScreen', return_value=None):
            dialog.center_on_screen()

    @patch("views.load_data_manual_dialog.QtWidgets.QFileDialog.getOpenFileName")
    def test_browse_database_sets_text(self, mock_get_file, app):
        dialog = LoadDataManualDialog()
        mock_get_file.return_value = ("/fake/path/database.accdb", "Access Databases (*.mdb *.accdb)")

        dialog.browse_database()
        
        assert dialog.txtDatabasePath.text() == "/fake/path/database.accdb"

    @patch("views.load_data_manual_dialog.QtWidgets.QFileDialog.getOpenFileName")
    def test_browse_database_cancelled(self, mock_get_file, app):
        dialog = LoadDataManualDialog()
        dialog.txtDatabasePath.setText("original_path.accdb")
        mock_get_file.return_value = ("", "")

        dialog.browse_database()
        
        assert dialog.txtDatabasePath.text() == "original_path.accdb"

    @patch("views.load_data_manual_dialog.get_db_connection")
    @patch("views.load_data_manual_dialog.load_emp_data")
    @patch("views.load_data_manual_dialog.load_team_data")
    def test_load_database_success(self, mock_team, mock_emp, mock_conn, app):
        dialog = LoadDataManualDialog()
        dialog.txtDatabasePath.setText("/fake/path/database.accdb")

        mock_conn.return_value = MagicMock()
        mock_emp.return_value = [{"id": 1, "name": "Alice"}]
        mock_team.return_value = [{"id": 1, "team": "Engineering"}]

        with patch.object(dialog, 'accept') as mock_accept:
            dialog.load_database()

            mock_conn.assert_called_once_with(db_path="/fake/path/database.accdb")
            mock_emp.assert_called_once()
            mock_team.assert_called_once()
            mock_accept.assert_called_once()
            assert hasattr(dialog, 'emp_data')
            assert hasattr(dialog, 'team_data')

    @patch("views.load_data_manual_dialog.get_db_connection")
    def test_load_database_no_connection(self, mock_conn, app):
        dialog = LoadDataManualDialog()
        dialog.txtDatabasePath.setText("/fake/path/database.accdb")
        mock_conn.return_value = None

        result = dialog.load_database()
        
        assert result is None
        assert not hasattr(dialog, 'emp_data')
        assert not hasattr(dialog, 'team_data')

    @patch("views.load_data_manual_dialog.get_db_connection")
    @patch("views.load_data_manual_dialog.load_emp_data")
    @patch("views.load_data_manual_dialog.load_team_data")
    @patch("views.load_data_manual_dialog.QtWidgets.QMessageBox.critical")
    def test_load_database_emp_data_error(self, mock_critical, mock_team, mock_emp, mock_conn, app):
        dialog = LoadDataManualDialog()
        dialog.txtDatabasePath.setText("/fake/path/database.accdb")

        mock_conn.return_value = MagicMock()
        mock_emp.side_effect = Exception("Employee data error")

        dialog.load_database()
        
        mock_critical.assert_called_once()
        assert "Employee data error" in mock_critical.call_args[0][2]

    @patch("views.load_data_manual_dialog.get_db_connection")
    @patch("views.load_data_manual_dialog.load_emp_data")
    @patch("views.load_data_manual_dialog.load_team_data")
    @patch("views.load_data_manual_dialog.QtWidgets.QMessageBox.critical")
    def test_load_database_team_data_error(self, mock_critical, mock_team, mock_emp, mock_conn, app):
        dialog = LoadDataManualDialog()
        dialog.txtDatabasePath.setText("/fake/path/database.accdb")

        mock_conn.return_value = MagicMock()
        mock_emp.return_value = [{"id": 1, "name": "Alice"}]
        mock_team.side_effect = Exception("Team data error")

        dialog.load_database()
        
        mock_critical.assert_called_once()
        assert "Team data error" in mock_critical.call_args[0][2]

    @patch("views.load_data_manual_dialog.get_db_connection")
    @patch("views.load_data_manual_dialog.load_emp_data")
    @patch("views.load_data_manual_dialog.load_team_data")
    def test_load_database_closes_connection(self, mock_team, mock_emp, mock_conn, app):
        dialog = LoadDataManualDialog()
        dialog.txtDatabasePath.setText("/fake/path/database.accdb")

        mock_connection = MagicMock()
        mock_conn.return_value = mock_connection
        mock_emp.return_value = [{"id": 1, "name": "Alice"}]
        mock_team.return_value = [{"id": 1, "team": "Engineering"}]

        dialog.load_database()

        mock_connection.close.assert_called_once()

    @patch("views.load_data_manual_dialog.get_db_connection")
    @patch("views.load_data_manual_dialog.load_emp_data")
    def test_load_database_closes_connection_on_error(self, mock_emp, mock_conn, app):
        dialog = LoadDataManualDialog()
        dialog.txtDatabasePath.setText("/fake/path/database.accdb")

        mock_connection = MagicMock()
        mock_conn.return_value = mock_connection
        mock_emp.side_effect = Exception("Test error")

        with patch.object(QtWidgets.QMessageBox, 'critical'):
            dialog.load_database()

        mock_connection.close.assert_called_once()

    def test_empty_database_path(self, app):
        dialog = LoadDataManualDialog()
        dialog.txtDatabasePath.setText("")

        with patch("views.load_data_manual_dialog.get_db_connection") as mock_conn, \
             patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
            dialog.load_database()
            
            mock_warning.assert_called_once()
            mock_conn.assert_not_called()
            assert "Input Required" in mock_warning.call_args[0][1]

    def test_whitespace_database_path(self, app):
        dialog = LoadDataManualDialog()
        dialog.txtDatabasePath.setText("   ")

        with patch("views.load_data_manual_dialog.get_db_connection") as mock_conn, \
             patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
            dialog.load_database()
            
            mock_warning.assert_called_once()
            mock_conn.assert_not_called()
            assert "Input Required" in mock_warning.call_args[0][1]