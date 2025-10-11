import sys
import pytest
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from views.load_data_dynamic_dialog import LoadDataDynamicDialog


@pytest.fixture(scope="session")
def app():
    """Create QApplication instance for testing."""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    return app


def test_center_on_screen_moves_dialog(app):
    """Test that center_on_screen properly positions the dialog."""
    dialog = LoadDataDynamicDialog()

    mock_screen = MagicMock()
    mock_screen.availableGeometry.return_value.width.return_value = 1920
    mock_screen.availableGeometry.return_value.height.return_value = 1080

    with patch.object(QtWidgets.QApplication, 'primaryScreen', return_value=mock_screen):
        dialog.center_on_screen()
        assert dialog.pos() is not None


def test_center_on_screen_no_screen(app):
    """Test center_on_screen handles missing screen gracefully."""
    dialog = LoadDataDynamicDialog()

    with patch.object(QtWidgets.QApplication, 'primaryScreen', return_value=None):
        dialog.center_on_screen()


@patch("views.load_data_dynamic_dialog.get_db_connection")
@patch("views.load_data_dynamic_dialog.load_emp_data")
@patch("views.load_data_dynamic_dialog.load_team_data")
@patch("views.load_data_dynamic_dialog.load_store_data")
def test_load_database_success(mock_store, mock_team, mock_emp, mock_conn, app):
    """Test successful database loading with job number."""
    dialog = LoadDataDynamicDialog()
    dialog.txtJobNumber.setText("TEST123")

    mock_conn.return_value = MagicMock()
    mock_store.return_value = {"store": "Test Store"}
    mock_emp.return_value = [{"id": 1, "name": "Alice"}]
    mock_team.return_value = [{"id": 1, "team": "Engineering"}]

    dialog.load_database()

    expected_path = r"C:\WISDOM\JOBS\TEST123\11355\TEST123.MDB"
    mock_conn.assert_called_once_with(db_path=expected_path)
    mock_store.assert_called_once()
    mock_emp.assert_called_once()
    mock_team.assert_called_once()
    assert hasattr(dialog, 'store_data')
    assert hasattr(dialog, 'emp_data')
    assert hasattr(dialog, 'team_data')


def test_load_database_empty_job_number_shows_warning(app):
    """Test that empty job number shows warning and returns early."""
    dialog = LoadDataDynamicDialog()
    dialog.txtJobNumber.setText("")

    with patch.object(QtWidgets.QMessageBox, 'warning') as mock_warning:
        dialog.load_database()
        mock_warning.assert_called_once()


def test_load_database_whitespace_job_number_shows_warning(app):
    """Test that whitespace-only job number shows warning and returns early."""
    dialog = LoadDataDynamicDialog()
    dialog.txtJobNumber.setText("   ")

    with patch.object(QtWidgets.QMessageBox, 'warning') as mock_warning:
        dialog.load_database()
        mock_warning.assert_called_once()


@patch("views.load_data_dynamic_dialog.get_db_connection")
def test_load_database_no_connection_rejects_dialog(mock_conn, app):
    """Test that failed connection rejects dialog."""
    dialog = LoadDataDynamicDialog()
    dialog.txtJobNumber.setText("TEST123")
    mock_conn.return_value = None

    with patch.object(dialog, 'reject') as mock_reject:
        dialog.load_database()
        mock_reject.assert_called_once()


@patch("views.load_data_dynamic_dialog.get_db_connection")
@patch("views.load_data_dynamic_dialog.load_emp_data")
def test_load_database_emp_data_error_handling(mock_emp, mock_conn, app):
    """Test error handling during employee data loading."""
    dialog = LoadDataDynamicDialog()
    dialog.txtJobNumber.setText("TEST123")

    mock_conn.return_value = MagicMock()
    mock_emp.side_effect = Exception("Database error")

    with patch.object(QtWidgets.QMessageBox, 'critical') as mock_critical:
        with patch.object(dialog, 'reject') as mock_reject:
            dialog.load_database()
            mock_critical.assert_called_once()
            mock_reject.assert_called_once()


@patch("views.load_data_dynamic_dialog.get_db_connection")
@patch("views.load_data_dynamic_dialog.load_emp_data")
@patch("views.load_data_dynamic_dialog.load_team_data")
def test_load_database_team_data_error_handling(mock_team, mock_emp, mock_conn, app):
    """Test error handling during team data loading."""
    dialog = LoadDataDynamicDialog()
    dialog.txtJobNumber.setText("TEST123")

    mock_conn.return_value = MagicMock()
    mock_emp.return_value = [{"id": 1, "name": "Alice"}]
    mock_team.side_effect = Exception("Team data error")

    with patch.object(QtWidgets.QMessageBox, 'critical') as mock_critical:
        with patch.object(dialog, 'reject') as mock_reject:
            dialog.load_database()
            mock_critical.assert_called_once()
            mock_reject.assert_called_once()


@patch("views.load_data_dynamic_dialog.get_db_connection")
@patch("views.load_data_dynamic_dialog.load_emp_data")
@patch("views.load_data_dynamic_dialog.load_team_data")
def test_load_database_closes_connection(mock_team, mock_emp, mock_conn, app):
    """Test that database connection is properly closed."""
    dialog = LoadDataDynamicDialog()
    dialog.txtJobNumber.setText("TEST123")

    mock_connection = MagicMock()
    mock_conn.return_value = mock_connection
    mock_emp.return_value = [{"id": 1, "name": "Alice"}]
    mock_team.return_value = [{"id": 1, "team": "Engineering"}]

    dialog.load_database()

    mock_connection.close.assert_called_once()


@patch("views.load_data_dynamic_dialog.get_db_connection")
@patch("views.load_data_dynamic_dialog.load_emp_data")
def test_load_database_closes_connection_on_error(mock_emp, mock_conn, app):
    """Test that database connection is closed even when error occurs."""
    dialog = LoadDataDynamicDialog()
    dialog.txtJobNumber.setText("TEST123")

    mock_connection = MagicMock()
    mock_conn.return_value = mock_connection
    mock_emp.side_effect = Exception("Test error")

    with patch.object(QtWidgets.QMessageBox, 'critical'):
        with patch.object(dialog, 'reject'):
            dialog.load_database()

    mock_connection.close.assert_called_once()


@patch("views.load_data_dynamic_dialog.get_db_connection")
@patch("views.load_data_dynamic_dialog.load_emp_data")
@patch("views.load_data_dynamic_dialog.load_team_data")
def test_load_database_sets_data_attributes(mock_team, mock_emp, mock_conn, app):
    """Test that employee and team data are properly set as attributes."""
    dialog = LoadDataDynamicDialog()
    dialog.txtJobNumber.setText("TEST123")

    emp_data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    team_data = [{"id": 1, "team": "Engineering"}, {"id": 2, "team": "Sales"}]

    mock_conn.return_value = MagicMock()
    mock_emp.return_value = emp_data
    mock_team.return_value = team_data

    dialog.load_database()

    assert dialog.emp_data == emp_data
    assert dialog.team_data == team_data


    def test_dialog_initialization(app):
        """Test that dialog initializes properly with UI components."""
        with patch("views.load_data_dynamic_dialog.resource_path") as mock_resource_path:
            mock_resource_path.return_value = "/fake/path/ui"
            
            def mock_load_ui(ui_path, dialog):
                dialog.btnLoad = MagicMock()
                dialog.txtJobNumber = MagicMock()
            
            with patch("views.load_data_dynamic_dialog.uic.loadUi", side_effect=mock_load_ui):
                dialog = LoadDataDynamicDialog()
                
                assert hasattr(dialog, 'btnLoad')
                assert hasattr(dialog, 'txtJobNumber')


@patch("views.load_data_dynamic_dialog.get_db_connection")
@patch("views.load_data_dynamic_dialog.load_emp_data")
@patch("views.load_data_dynamic_dialog.load_team_data")
def test_load_database_accepts_dialog_on_success(mock_team, mock_emp, mock_conn, app):
    """Test that dialog accepts when data loading succeeds."""
    dialog = LoadDataDynamicDialog()
    dialog.txtJobNumber.setText("TEST123")

    mock_conn.return_value = MagicMock()
    mock_emp.return_value = [{"id": 1, "name": "Alice"}]
    mock_team.return_value = [{"id": 1, "team": "Engineering"}]

    with patch.object(dialog, 'accept') as mock_accept:
        dialog.load_database()
        mock_accept.assert_called_once()
