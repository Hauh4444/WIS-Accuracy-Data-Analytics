import pytest
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from views.stats_source_dialog import StatsSourceDialog


@pytest.fixture
def qt_app(qtbot):
    """Ensure a QApplication instance exists for tests."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app


@patch("stats_source_dialog.get_storage_db_connection")
@patch("stats_source_dialog.load_local_store_data")
@patch("stats_source_dialog.load_local_emp_data")
@patch("stats_source_dialog.load_local_zone_data")
@patch("stats_source_dialog.generate_accuracy_report")
def test_load_season_stats_success(mock_generate, mock_zone, mock_emp, mock_store, mock_conn, qt_app, qtbot):
    store_data = {"store": "Store 123"}
    emp_data = [{"emp_number": "E001", "emp_name": "Alice"}]
    zone_data = [{"zone_id": "Z1"}]

    mock_conn.return_value = MagicMock()
    mock_store.return_value = store_data
    mock_emp.return_value = emp_data
    mock_zone.return_value = zone_data

    dialog = StatsSourceDialog()
    qtbot.addWidget(dialog)

    dialog.load_season_stats()

    assert dialog.source == "season"
    mock_generate.assert_called_once_with(store_data=store_data, emp_data=emp_data, zone_data=zone_data)


@patch("stats_source_dialog.get_storage_db_connection")
def test_load_season_stats_no_connection(mock_conn, qt_app, qtbot):
    mock_conn.return_value = None
    dialog = StatsSourceDialog()
    qtbot.addWidget(dialog)

    dialog.load_season_stats()

    assert dialog.source == "season"


def test_load_old_stats_sets_source(qt_app, qtbot):
    dialog = StatsSourceDialog()
    qtbot.addWidget(dialog)

    dialog.load_old_stats()
    assert dialog.source == "local"


def test_load_new_stats_sets_source(qt_app, qtbot):
    dialog = StatsSourceDialog()
    qtbot.addWidget(dialog)

    dialog.load_new_stats()
    assert dialog.source == "source"


def test_get_result_returns_source(qt_app, qtbot):
    dialog = StatsSourceDialog()
    qtbot.addWidget(dialog)

    dialog.source = "test_source"
    result = dialog.get_result()
    assert result == "test_source"


@patch("stats_source_dialog.get_storage_db_connection")
@patch("stats_source_dialog.load_local_store_data")
@patch("stats_source_dialog.load_local_emp_data")
@patch("stats_source_dialog.load_local_zone_data")
@patch("stats_source_dialog.generate_accuracy_report")
def test_load_season_stats_exception_handling(mock_generate, mock_zone, mock_emp, mock_store, mock_conn, qt_app, qtbot):
    """Test that exceptions during data load do not raise and the dialog handles them gracefully."""
    mock_conn.return_value = MagicMock()
    mock_store.side_effect = Exception("DB error")

    dialog = StatsSourceDialog()
    qtbot.addWidget(dialog)

    dialog.load_season_stats()
    assert dialog.source == "season"
