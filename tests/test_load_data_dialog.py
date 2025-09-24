import sys
import pytest
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from views.load_data_dialog import LoadDataDialog


@pytest.fixture(scope="session")
def app():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    return app


def test_center_on_screen_moves_dialog(app):
    dialog = LoadDataDialog()

    mock_screen = MagicMock()
    mock_screen.availableGeometry.return_value.width.return_value = 1920
    mock_screen.availableGeometry.return_value.height.return_value = 1080

    with patch.object(QtWidgets.QApplication, 'primaryScreen', return_value=mock_screen):
        dialog.center_on_screen()
        assert dialog.pos() is not None


@patch("views.load_data_dialog.QtWidgets.QFileDialog.getOpenFileName")
def test_browse_database_sets_text(mock_get_file, app):
    dialog = LoadDataDialog()
    mock_get_file.return_value = ("/fake/path/database.accdb", "Access Databases (*.mdb *.accdb)")

    dialog.browse_database()
    assert dialog.txtDatabasePath.text() == "/fake/path/database.accdb"


@patch("views.load_data_dialog.get_db_connection")
@patch("views.load_data_dialog.load_emp_data")
@patch("views.load_data_dialog.load_team_data")
def test_on_load_clicked_success(mock_team, mock_emp, mock_conn, app):
    dialog = LoadDataDialog()
    dialog.txtDatabasePath.setText("/fake/path/database.accdb")

    mock_conn.return_value = MagicMock()
    mock_emp.return_value = [{"id": 1, "name": "Alice"}]
    mock_team.return_value = [{"id": 1, "team": "Engineering"}]

    with patch("views.load_data_dialog.EmpHoursInputWindow") as mock_window_class:
        mock_window_instance = MagicMock()
        mock_window_class.return_value = mock_window_instance

        dialog.on_load_clicked()

        mock_conn.assert_called_once_with(db_path="/fake/path/database.accdb")
        mock_emp.assert_called_once()
        mock_team.assert_called_once()
        mock_window_class.assert_called_once_with(mock_emp.return_value, mock_team.return_value)
        mock_window_instance.show.assert_called_once()


@patch("views.load_data_dialog.get_db_connection")
def test_on_load_clicked_no_connection_shows_nothing(mock_conn, app):
    dialog = LoadDataDialog()
    dialog.txtDatabasePath.setText("/fake/path/database.accdb")
    mock_conn.return_value = None

    result = dialog.on_load_clicked()
    assert result is None


@patch("views.load_data_dialog.get_db_connection")
@patch("views.load_data_dialog.load_emp_data")
@patch("views.load_data_dialog.load_team_data")
@patch("views.load_data_dialog.QtWidgets.QMessageBox.critical")
def test_on_load_clicked_raises_error_shows_message(mock_msg, mock_team, mock_emp, mock_conn, app):
    dialog = LoadDataDialog()
    dialog.txtDatabasePath.setText("/fake/path/database.accdb")

    mock_conn.return_value = MagicMock()
    mock_emp.side_effect = Exception("Test Exception")

    dialog.on_load_clicked()
    mock_msg.assert_called_once()
    assert "Test Exception" in mock_msg.call_args[0][2]

