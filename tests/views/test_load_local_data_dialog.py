import pytest
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from views.load_local_data_dialog import LoadLocalDataDialog


@pytest.fixture
def qt_app(qtbot):
    """Ensure a QApplication instance exists for tests."""
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
    dialog = LoadLocalDataDialog()
    qtbot.addWidget(dialog)

    assert hasattr(dialog, "txtJobNumber")
    assert hasattr(dialog, "btnLoad")
    assert dialog.btnLoad.isEnabled()


@patch("load_local_data_dialog.get_storage_db_connection")
@patch("load_local_data_dialog.load_local_store_data")
@patch("load_local_data_dialog.load_local_emp_data")
@patch("load_local_data_dialog.load_local_zone_data")
def test_load_database_success(mock_zone, mock_emp, mock_store, mock_conn, qt_app, qtbot, sample_data):
    store_data, emp_data, zone_data = sample_data
    mock_conn.return_value = MagicMock()
    mock_store.return_value = store_data
    mock_emp.return_value = emp_data
    mock_zone.return_value = zone_data

    dialog = LoadLocalDataDialog()
    qtbot.addWidget(dialog)
    dialog.txtJobNumber.setText("JOB123")

    dialog.load_database()

    assert dialog.store_data == store_data
    assert dialog.emp_data == emp_data
    assert dialog.zone_data == zone_data


def test_load_database_no_job_number_shows_warning(qt_app, qtbot):
    dialog = LoadLocalDataDialog()
    qtbot.addWidget(dialog)
    dialog.txtJobNumber.setText("")

    with patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
        dialog.load_database()
        mock_warning.assert_called_once_with(dialog, "Input Required", "Please enter a Job Number.")


@patch("load_local_data_dialog.get_storage_db_connection")
def test_load_database_connection_failure(mock_conn, qt_app, qtbot):
    mock_conn.return_value = None
    dialog = LoadLocalDataDialog()
    qtbot.addWidget(dialog)
    dialog.txtJobNumber.setText("JOB123")

    dialog.load_database()

    assert not hasattr(dialog, "store_data")
    assert not hasattr(dialog, "emp_data")
    assert not hasattr(dialog, "zone_data")


@patch("load_local_data_dialog.get_storage_db_connection")
@patch("load_local_data_dialog.load_local_store_data")
def test_load_database_exception_handling(mock_store, mock_conn, qt_app, qtbot):
    mock_conn.return_value = MagicMock()
    mock_store.side_effect = Exception("Database error")

    dialog = LoadLocalDataDialog()
    qtbot.addWidget(dialog)
    dialog.txtJobNumber.setText("JOB123")

    dialog.load_database()

    assert not hasattr(dialog, "store_data")
    assert not hasattr(dialog, "emp_data")
    assert not hasattr(dialog, "zone_data")


def test_get_data_returns_correct_tuple(qt_app, qtbot, sample_data):
    store_data, emp_data, zone_data = sample_data
    dialog = LoadLocalDataDialog()
    qtbot.addWidget(dialog)

    dialog.store_data = store_data
    dialog.emp_data = emp_data
    dialog.zone_data = zone_data

    result = dialog.get_data()
    assert result == (store_data, emp_data, zone_data)
