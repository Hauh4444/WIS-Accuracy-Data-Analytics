import pytest
import sys
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from views.stats_source_dialog import StatsSourceDialog


@pytest.fixture
def q_app():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    yield app
    for widget in app.topLevelWidgets():
        widget.close()
    app.processEvents()


@pytest.fixture
def dialog(q_app):
    dlg = StatsSourceDialog.__new__(StatsSourceDialog)
    QtWidgets.QDialog.__init__(dlg)
    dlg.btnRange = MagicMock(spec=QtWidgets.QPushButton)
    dlg.btnOld = MagicMock(spec=QtWidgets.QPushButton)
    dlg.btnNew = MagicMock(spec=QtWidgets.QPushButton)
    dlg.accept = MagicMock()
    dlg.reject = MagicMock()
    return dlg


@pytest.fixture
def sample_data():
    store_data = {"store": "Store 123"}
    emp_data = [{"emp_number": "E001", "emp_name": "Alice"}]
    zone_data = [{"zone_id": "Z1"}]
    return store_data, emp_data, zone_data


def test_load_aggregate_stats_success(dialog, sample_data):
    store_data, emp_data, zone_data = sample_data

    with patch("views.stats_source_dialog.get_storage_db_connection", return_value=MagicMock()) as mock_conn, \
         patch("views.stats_source_dialog.load_local_store_data", return_value=store_data), \
         patch("views.stats_source_dialog.load_local_emp_data", return_value=emp_data), \
         patch("views.stats_source_dialog.load_local_zone_data", return_value=zone_data), \
         patch("views.stats_source_dialog.generate_accuracy_report") as mock_generate:

        dialog.load_aggregate_stats()

        assert dialog.source == "aggregate"
        mock_generate.assert_called_once_with(store_data, emp_data, zone_data, aggregate=True)
        dialog.accept.assert_called_once()


def test_load_aggregate_stats_no_connection(dialog):
    with patch("views.stats_source_dialog.get_storage_db_connection", return_value=None):
        dialog.load_aggregate_stats()
        dialog.reject.assert_called_once()


def test_load_aggregate_stats_exception_handling(dialog):
    with patch("views.stats_source_dialog.get_storage_db_connection", return_value=MagicMock()) as mock_conn, \
         patch("views.stats_source_dialog.load_local_store_data", side_effect=Exception("DB error")), \
         patch("views.stats_source_dialog.load_local_emp_data"), \
         patch("views.stats_source_dialog.load_local_zone_data"), \
         patch("views.stats_source_dialog.generate_accuracy_report") as mock_generate:

        import pytest
        with pytest.raises(Exception, match="DB error"):
            dialog.load_aggregate_stats()

        mock_generate.assert_not_called()
        dialog.accept.assert_not_called()


def test_load_old_stats_sets_source(dialog):
    dialog.load_old_stats()
    assert dialog.source == "local"
    dialog.accept.assert_called_once()


def test_load_new_stats_sets_source(dialog):
    dialog.load_new_stats()
    assert dialog.source == "source"
    dialog.accept.assert_called_once()


def test_get_result_returns_source(dialog):
    dialog.source = "test_source"
    assert dialog.get_result() == "test_source"
