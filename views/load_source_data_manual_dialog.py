"""Manual database loading dialog with file browser."""
from PyQt6 import QtWidgets, uic

from database import get_db_connection
from utils import resource_path
from utils import center_on_screen
from services import load_source_store_data, load_source_emp_data, load_source_zone_data


class LoadSourceDataManualDialog(QtWidgets.QDialog):
    """Dialog for loading database using file browser."""
    txtDatabasePath: QtWidgets.QLineEdit
    btnBrowse: QtWidgets.QPushButton
    btnLoad: QtWidgets.QPushButton

    store_data: dict
    emp_data: list[dict]
    zone_data: list[dict]

    def __init__(self) -> None:
        """Initialize the dialog and connect UI elements."""
        super().__init__()
        ui_path = resource_path("assets/ui/load_source_data_manual_dialog.ui")
        uic.loadUi(ui_path, self)

        self.btnBrowse.clicked.connect(self.browse_database)
        self.btnLoad.clicked.connect(self.load_database)

        center_on_screen(widget=self)

    def browse_database(self) -> None:
        """Open file dialog to select database file."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            parent=self,
            caption="Select Database File",
            directory=r"C:\WISDOM\JOBS",
            filter="Access Databases (*.mdb *.accdb);;All Files (*)"
        )
        if file_path:
            self.txtDatabasePath.setText(file_path)

    def load_database(self) -> None:
        """Load employee and zone data from selected database file."""
        db_path = self.txtDatabasePath.text().strip()
        if not db_path:
            QtWidgets.QMessageBox.warning(self, "Input Required", "Please enter a Database Path.")
            return

        conn = get_db_connection(db_path)
        if not conn:
            self.reject()
            return

        self.store_data = load_source_store_data(conn)
        self.emp_data = load_source_emp_data(conn)
        self.zone_data = load_source_zone_data(conn)

        conn.close()
        self.accept()

    def get_data(self):
        return self.store_data, self.emp_data, self.zone_data