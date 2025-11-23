import pytest
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from views.load_source_data_manual_dialog import LoadSourceDataManualDialog


@pytest.fixture
def qt_app(qtbot):
    """Ensure a QApplication instance exists."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app

@pytest.fixture
def sample_data():
    store_data = {"store": "Store 123"}
    emp_data = [{"emp_number": "E001", "emp_name": "Alice"}]
    zone_data = [{"zone_id": "Z1"}]
    return store_data, emp_data, zone_data


def test_dialog_initialization(qt_app, qtbot):
    dialog = LoadSourceDataManualDialog()
    qtbot.addWidget(dialog)

    assert hasattr(dialog, "txtDatabasePath")
    assert hasattr(dialog, "btnBrowse")
    assert hasattr(dialog, "btnLoad")
    assert dialog.btnLoad.isEnabled()


@patch("load_data_manual_dialog.get_db_connection")
@patch("load_data_manual_dialog.load_source_store_data")
@patch("load_data_manual_dialog.load_source_emp_data")
@patch("load_data_manual_dialog.load_source_zone_data")
def test_load_database_success(mock_zone, mock_emp, mock_store, mock_conn, qt_app, qtbot, sample_data):
    store_data, emp_data, zone_data = sample_data
    mock_conn.return_value = MagicMock()
    mock_store.return_value = store_data
    mock_emp.return_value = emp_data
    mock_zone.return_value = zone_data

    dialog = LoadSourceDataManualDialog()
    qtbot.addWidget(dialog)
    dialog.txtDatabasePath.setText("C:/fake/path/to/db.mdb")

    dialog.load_database()

    assert dialog.store_data == store_data
    assert dialog.emp_data == emp_data
    assert dialog.zone_data == zone_data


@patch("load_data_manual_dialog.QFileDialog.getOpenFileName")
def test_browse_database_sets_path(mock_file_dialog, qt_app, qtbot):
    dialog = LoadSourceDataManualDialog()
    qtbot.addWidget(dialog)

    mock_file_dialog.return_value = ("C:/fake/path/to/db.mdb", "Access Databases (*.mdb *.accdb)")
    dialog.browse_database()

    assert dialog.txtDatabasePath.text() == "C:/fake/path/to/db.mdb"


def test_load_database_no_path_shows_warning(qt_app, qtbot):
    dialog = LoadSourceDataManualDialog()
    qtbot.addWidget(dialog)
    dialog.txtDatabasePath.setText("")

    with patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        dialog.load_database()
        mock_warning.assert_called_once_with(dialog, "Input Required", "Please enter a Database Path.")


@patch("load_data_manual_dialog.get_db_connection")
def test_load_database_connection_failure(mock_conn, qt_app, qtbot):
    mock_conn.return_value = None
    dialog = LoadSourceDataManualDialog()
    qtbot.addWidget(dialog)
    dialog.txtDatabasePath.setText("C:/fake/path/to/db.mdb")

    dialog.load_database()

    assert not hasattr(dialog, "store_data")
    assert not hasattr(dialog, "emp_data")
    assert not hasattr(dialog, "zone_data")


@patch("load_data_manual_dialog.get_db_connection")
@patch("load_data_manual_dialog.load_source_store_data")
def test_load_database_exception_handling(mock_store, mock_conn, qt_app, qtbot):
    mock_conn.return_value = MagicMock()
    mock_store.side_effect = Exception("Database error")

    dialog = LoadSourceDataManualDialog()
    qtbot.addWidget(dialog)
    dialog.txtDatabasePath.setText("C:/fake/path/to/db.mdb")

    dialog.load_database()

    assert not hasattr(dialog, "store_data")
    assert not hasattr(dialog, "emp_data")
    assert not hasattr(dialog, "zone_data")


def test_get_data_returns_correct_tuple(qt_app, qtbot, sample_data):
    store_data, emp_data, zone_data = sample_data
    dialog = LoadSourceDataManualDialog()
    qtbot.addWidget(dialog)

    dialog.store_data = store_data
    dialog.emp_data = emp_data
    dialog.zone_data = zone_data

    result = dialog.get_data()
    assert result == (store_data, emp_data, zone_data)
