"""Dynamic database loading dialog using WISDOM job number convention."""
from PyQt6 import QtWidgets, uic

from database import get_storage_db_connection
from utils import resource_path
from utils import center_on_screen
from services import load_local_store_data, load_local_emp_data, load_local_zone_data


class LoadLocalDataDialog(QtWidgets.QDialog):
    """Dialog for loading database using job number input."""
    txtStoreNumber: QtWidgets.QLineEdit
    btnLoad: QtWidgets.QPushButton

    store_data: dict
    emp_data: list[dict]
    zone_data: list[dict]

    def __init__(self) -> None:
        """Initialize the dialog and connect UI elements."""
        super().__init__()
        ui_path = resource_path("assets/ui/load_local_data_dialog.ui")
        uic.loadUi(ui_path, self)

        self.btnLoad.clicked.connect(self.load_database)

        center_on_screen(widget=self)

    def load_database(self) -> None:
        """Load database from local appdata path"""
        store_number = self.txtStoreNumber.text().strip()
        if not store_number:
            QtWidgets.QMessageBox.warning(self, "Input Required", "Please enter a Store Number.")
            return

        conn = get_storage_db_connection()
        if not conn:
            self.reject()
            return

        self.store_data = load_local_store_data(conn, store_number)
        self.emp_data = load_local_emp_data(conn, store_number)
        self.zone_data = load_local_zone_data(conn, store_number)

        conn.close()
        self.accept()