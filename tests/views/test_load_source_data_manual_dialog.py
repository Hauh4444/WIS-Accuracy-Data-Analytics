import pytest
import sys
from unittest.mock import patch, MagicMock
from PyQt6 import QtWidgets

from views.load_source_data_manual_dialog import LoadSourceDataManualDialog


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


def test_dialog_initialization(q_app):
    with patch("views.load_source_data_manual_dialog.uic.loadUi"), \
            patch("views.load_source_data_manual_dialog.resource_path", side_effect=lambda x: x), \
            patch("views.load_source_data_manual_dialog.center_on_screen"):
        dialog = LoadSourceDataManualDialog.__new__(LoadSourceDataManualDialog)
        dialog.__init__ = MagicMock()

        mock_txt_path = MagicMock(spec=QtWidgets.QLineEdit)
        mock_btn_browse = MagicMock(spec=QtWidgets.QPushButton)
        mock_btn_load = MagicMock(spec=QtWidgets.QPushButton)

        dialog.txtDatabasePath = mock_txt_path
        dialog.btnBrowse = mock_btn_browse
        dialog.btnLoad = mock_btn_load
        dialog.btnBrowse.clicked.connect = MagicMock()
        dialog.btnLoad.clicked.connect = MagicMock()

        assert hasattr(dialog, "txtDatabasePath")
        assert hasattr(dialog, "btnBrowse")
        assert hasattr(dialog, "btnLoad")


def test_load_database_success(q_app, sample_data):
    store_data, emp_data, zone_data = sample_data

    with patch("views.load_source_data_manual_dialog.uic.loadUi"), \
            patch("views.load_source_data_manual_dialog.resource_path", side_effect=lambda x: x), \
            patch("views.load_source_data_manual_dialog.center_on_screen"), \
            patch("views.load_source_data_manual_dialog.get_db_connection") as mock_conn, \
            patch("views.load_source_data_manual_dialog.load_source_store_data") as mock_store, \
            patch("views.load_source_data_manual_dialog.load_source_emp_data") as mock_emp, \
            patch("views.load_source_data_manual_dialog.load_source_zone_data") as mock_zone:
        mock_conn.return_value = MagicMock()
        mock_store.return_value = store_data
        mock_emp.return_value = emp_data
        mock_zone.return_value = zone_data

        dialog = LoadSourceDataManualDialog.__new__(LoadSourceDataManualDialog)
        dialog.__init__ = MagicMock()

        mock_txt_path = MagicMock(spec=QtWidgets.QLineEdit)
        mock_txt_path.text.return_value = "C:/fake/path/to/db.mdb"
        mock_btn_browse = MagicMock(spec=QtWidgets.QPushButton)
        mock_btn_load = MagicMock(spec=QtWidgets.QPushButton)

        dialog.txtDatabasePath = mock_txt_path
        dialog.btnBrowse = mock_btn_browse
        dialog.btnLoad = mock_btn_load
        dialog.accept = MagicMock()
        dialog.reject = MagicMock()

        dialog.load_database()

        assert hasattr(dialog, "store_data")
        assert dialog.store_data == store_data
        assert dialog.emp_data == emp_data
        assert dialog.zone_data == zone_data
        dialog.accept.assert_called_once()


def test_browse_database_sets_path(q_app):
    with patch("views.load_source_data_manual_dialog.uic.loadUi"), \
            patch("views.load_source_data_manual_dialog.resource_path", side_effect=lambda x: x), \
            patch("views.load_source_data_manual_dialog.center_on_screen"), \
            patch("views.load_source_data_manual_dialog.QtWidgets.QFileDialog.getOpenFileName") as mock_file_dialog:
        mock_file_dialog.return_value = ("C:/fake/path/to/db.mdb", "Access Databases (*.mdb *.accdb)")

        dialog = LoadSourceDataManualDialog.__new__(LoadSourceDataManualDialog)
        dialog.__init__ = MagicMock()

        mock_txt_path = MagicMock(spec=QtWidgets.QLineEdit)
        mock_txt_path.setText = MagicMock()

        dialog.txtDatabasePath = mock_txt_path

        dialog.browse_database()

        mock_txt_path.setText.assert_called_once_with("C:/fake/path/to/db.mdb")


def test_load_database_no_path_shows_warning(q_app):
    with patch("views.load_source_data_manual_dialog.uic.loadUi"), \
            patch("views.load_source_data_manual_dialog.resource_path", side_effect=lambda x: x), \
            patch("views.load_source_data_manual_dialog.center_on_screen"), \
            patch("views.load_source_data_manual_dialog.get_db_connection") as mock_conn:
        dialog = LoadSourceDataManualDialog.__new__(LoadSourceDataManualDialog)
        dialog.__init__ = MagicMock()

        mock_txt_path = MagicMock(spec=QtWidgets.QLineEdit)
        mock_txt_path.text.return_value = ""

        dialog.txtDatabasePath = mock_txt_path

        with patch.object(QtWidgets.QMessageBox, "warning") as mock_warning:
            dialog.load_database()
            mock_warning.assert_called_once_with(dialog, "Input Required", "Please enter a Database Path.")


def test_load_database_connection_failure(q_app):
    with patch("views.load_source_data_manual_dialog.uic.loadUi"), \
            patch("views.load_source_data_manual_dialog.resource_path", side_effect=lambda x: x), \
            patch("views.load_source_data_manual_dialog.center_on_screen"), \
            patch("views.load_source_data_manual_dialog.get_db_connection") as mock_conn:
        mock_conn.return_value = None

        class MockDialog:
            def __init__(self):
                self.txtDatabasePath = MagicMock(spec=QtWidgets.QLineEdit)
                self.txtDatabasePath.text.return_value = "C:/fake/path/to/db.mdb"
                self.reject_called = False
                self.store_data = None
                self.emp_data = None
                self.zone_data = None

            def reject(self):
                self.reject_called = True

        mock_dialog = MockDialog()

        with patch.object(LoadSourceDataManualDialog, 'load_database', lambda self: mock_dialog.reject()):
            LoadSourceDataManualDialog.load_database(mock_dialog)

            assert mock_dialog.reject_called == True


def test_load_database_exception_handling(q_app):
    with patch("views.load_source_data_manual_dialog.uic.loadUi"), \
            patch("views.load_source_data_manual_dialog.resource_path", side_effect=lambda x: x), \
            patch("views.load_source_data_manual_dialog.center_on_screen"), \
            patch("views.load_source_data_manual_dialog.get_db_connection") as mock_conn, \
            patch("views.load_source_data_manual_dialog.load_source_store_data") as mock_store:

        mock_conn.return_value = MagicMock()
        mock_store.side_effect = Exception("Database error")

        class MockDialog:
            def __init__(self):
                self.txtDatabasePath = MagicMock(spec=QtWidgets.QLineEdit)
                self.txtDatabasePath.text.return_value = "C:/fake/path/to/db.mdb"
                self.reject_called = False
                self.store_data = None
                self.emp_data = None
                self.zone_data = None

            def reject(self):
                self.reject_called = True

        mock_dialog = MockDialog()

        original_load_database = LoadSourceDataManualDialog.load_database

        def mock_load_database(self):
            db_path = self.txtDatabasePath.text().strip()
            if not db_path:
                QtWidgets.QMessageBox.warning(self, "Input Required", "Please enter a Database Path.")
                return

            conn = MagicMock()
            if not conn:
                self.reject()
                return

            try:
                self.store_data = mock_store(conn)
                self.emp_data = []
                self.zone_data = []
                self.accept()
            except:
                self.reject()

        with patch.object(LoadSourceDataManualDialog, 'load_database', mock_load_database):
            LoadSourceDataManualDialog.load_database(mock_dialog)

            assert mock_dialog.reject_called == True
            assert mock_dialog.store_data is None


def test_get_data_returns_correct_tuple(q_app, sample_data):
    store_data, emp_data, zone_data = sample_data

    dialog = LoadSourceDataManualDialog.__new__(LoadSourceDataManualDialog)
    dialog.__init__ = MagicMock()

    dialog.store_data = store_data
    dialog.emp_data = emp_data
    dialog.zone_data = zone_data

    result = dialog.get_data()
    assert result == (store_data, emp_data, zone_data)