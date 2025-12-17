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
def sample_data():
    store_data = {"store": "Store 123"}
    emp_data = [{"emp_number": "E001", "emp_name": "Alice"}]
    zone_data = [{"zone_id": "Z1"}]
    return store_data, emp_data, zone_data


def test_load_season_stats_success(q_app, sample_data):
    store_data, emp_data, zone_data = sample_data

    with patch("views.stats_source_dialog.uic.loadUi"), \
            patch("views.stats_source_dialog.resource_path", side_effect=lambda x: x), \
            patch("views.stats_source_dialog.center_on_screen"), \
            patch("views.stats_source_dialog.get_storage_db_connection") as mock_conn, \
            patch("views.stats_source_dialog.load_local_store_data") as mock_store, \
            patch("views.stats_source_dialog.load_local_emp_data") as mock_emp, \
            patch("views.stats_source_dialog.load_local_zone_data") as mock_zone, \
            patch("views.stats_source_dialog.generate_accuracy_report") as mock_generate:

        mock_conn.return_value = MagicMock()
        mock_store.return_value = store_data
        mock_emp.return_value = emp_data
        mock_zone.return_value = zone_data

        dialog = StatsSourceDialog.__new__(StatsSourceDialog)
        dialog.__init__ = MagicMock()
        dialog.source = None

        mock_btn_season = MagicMock(spec=QtWidgets.QPushButton)
        mock_btn_old = MagicMock(spec=QtWidgets.QPushButton)
        mock_btn_new = MagicMock(spec=QtWidgets.QPushButton)

        dialog.btnSeason = mock_btn_season
        dialog.btnOld = mock_btn_old
        dialog.btnNew = mock_btn_new
        dialog.btnSeason.clicked.connect = MagicMock()
        dialog.btnOld.clicked.connect = MagicMock()
        dialog.btnNew.clicked.connect = MagicMock()
        dialog.accept = MagicMock()
        dialog.reject = MagicMock()

        dialog.load_season_stats()

        assert dialog.source == "season"
        mock_generate.assert_called_once_with(store_data, emp_data, zone_data, season=True)
        dialog.accept.assert_called_once()


def test_load_season_stats_no_connection(q_app):
    with patch("views.stats_source_dialog.uic.loadUi"), \
            patch("views.stats_source_dialog.resource_path", side_effect=lambda x: x), \
            patch("views.stats_source_dialog.center_on_screen"), \
            patch("views.stats_source_dialog.get_storage_db_connection") as mock_conn:

        mock_conn.return_value = None

        dialog = StatsSourceDialog.__new__(StatsSourceDialog)
        dialog.__init__ = MagicMock()
        dialog.source = None

        mock_btn_season = MagicMock(spec=QtWidgets.QPushButton)
        mock_btn_old = MagicMock(spec=QtWidgets.QPushButton)
        mock_btn_new = MagicMock(spec=QtWidgets.QPushButton)

        dialog.btnSeason = mock_btn_season
        dialog.btnOld = mock_btn_old
        dialog.btnNew = mock_btn_new
        dialog.btnSeason.clicked.connect = MagicMock()
        dialog.btnOld.clicked.connect = MagicMock()
        dialog.btnNew.clicked.connect = MagicMock()
        dialog.reject = MagicMock()

        dialog.load_season_stats()

        dialog.reject.assert_called_once()


def test_load_old_stats_sets_source(q_app):
    with patch("views.stats_source_dialog.uic.loadUi"), \
            patch("views.stats_source_dialog.resource_path", side_effect=lambda x: x), \
            patch("views.stats_source_dialog.center_on_screen"):

        dialog = StatsSourceDialog.__new__(StatsSourceDialog)
        dialog.__init__ = MagicMock()
        dialog.source = None

        mock_btn_season = MagicMock(spec=QtWidgets.QPushButton)
        mock_btn_old = MagicMock(spec=QtWidgets.QPushButton)
        mock_btn_new = MagicMock(spec=QtWidgets.QPushButton)

        dialog.btnSeason = mock_btn_season
        dialog.btnOld = mock_btn_old
        dialog.btnNew = mock_btn_new
        dialog.btnSeason.clicked.connect = MagicMock()
        dialog.btnOld.clicked.connect = MagicMock()
        dialog.btnNew.clicked.connect = MagicMock()
        dialog.accept = MagicMock()

        dialog.load_old_stats()

        assert dialog.source == "local"
        dialog.accept.assert_called_once()


def test_load_new_stats_sets_source(q_app):
    with patch("views.stats_source_dialog.uic.loadUi"), \
            patch("views.stats_source_dialog.resource_path", side_effect=lambda x: x), \
            patch("views.stats_source_dialog.center_on_screen"):

        dialog = StatsSourceDialog.__new__(StatsSourceDialog)
        dialog.__init__ = MagicMock()
        dialog.source = None

        mock_btn_season = MagicMock(spec=QtWidgets.QPushButton)
        mock_btn_old = MagicMock(spec=QtWidgets.QPushButton)
        mock_btn_new = MagicMock(spec=QtWidgets.QPushButton)

        dialog.btnSeason = mock_btn_season
        dialog.btnOld = mock_btn_old
        dialog.btnNew = mock_btn_new
        dialog.btnSeason.clicked.connect = MagicMock()
        dialog.btnOld.clicked.connect = MagicMock()
        dialog.btnNew.clicked.connect = MagicMock()
        dialog.accept = MagicMock()

        dialog.load_new_stats()

        assert dialog.source == "source"
        dialog.accept.assert_called_once()


def test_get_result_returns_source(q_app):
    with patch("views.stats_source_dialog.uic.loadUi"), \
            patch("views.stats_source_dialog.resource_path", side_effect=lambda x: x), \
            patch("views.stats_source_dialog.center_on_screen"):

        dialog = StatsSourceDialog.__new__(StatsSourceDialog)
        dialog.__init__ = MagicMock()
        dialog.source = None

        mock_btn_season = MagicMock(spec=QtWidgets.QPushButton)
        mock_btn_old = MagicMock(spec=QtWidgets.QPushButton)
        mock_btn_new = MagicMock(spec=QtWidgets.QPushButton)

        dialog.btnSeason = mock_btn_season
        dialog.btnOld = mock_btn_old
        dialog.btnNew = mock_btn_new
        dialog.btnSeason.clicked.connect = MagicMock()
        dialog.btnOld.clicked.connect = MagicMock()
        dialog.btnNew.clicked.connect = MagicMock()

        dialog.source = "test_source"
        result = dialog.get_result()

        assert result == "test_source"


def test_load_season_stats_exception_handling(q_app):
    with patch("views.stats_source_dialog.uic.loadUi"), \
            patch("views.stats_source_dialog.resource_path", side_effect=lambda x: x), \
            patch("views.stats_source_dialog.center_on_screen"), \
            patch("views.stats_source_dialog.get_storage_db_connection") as mock_conn, \
            patch("views.stats_source_dialog.load_local_store_data") as mock_store:

        mock_conn.return_value = MagicMock()
        mock_store.side_effect = Exception("DB error")

        dialog = StatsSourceDialog.__new__(StatsSourceDialog)
        dialog.__init__ = MagicMock()
        dialog.source = None

        mock_btn_season = MagicMock(spec=QtWidgets.QPushButton)
        mock_btn_old = MagicMock(spec=QtWidgets.QPushButton)
        mock_btn_new = MagicMock(spec=QtWidgets.QPushButton)

        dialog.btnSeason = mock_btn_season
        dialog.btnOld = mock_btn_old
        dialog.btnNew = mock_btn_new
        dialog.btnSeason.clicked.connect = MagicMock()
        dialog.btnOld.clicked.connect = MagicMock()
        dialog.btnNew.clicked.connect = MagicMock()
        dialog.accept = MagicMock()

        dialog.load_season_stats()

        assert dialog.source == "season"
        dialog.accept.assert_not_called()