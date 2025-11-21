"""Manual database loading dialog with file browser."""
import traceback
from PyQt6 import QtWidgets, uic

from database.connection import get_db_connection
from utils.paths import resource_path
from utils.ui_utils import center_on_screen
from services.load_source_store_data import load_source_store_data
from services.load_source_emp_data import load_source_emp_data
from services.load_source_team_data import load_source_team_data
from services.save_local_data import save_local_data


class LoadDataManualDialog(QtWidgets.QDialog):
    """Dialog for loading database using file browser."""
    txtDatabasePath: QtWidgets.QLineEdit
    btnBrowse: QtWidgets.QPushButton
    btnLoad: QtWidgets.QPushButton

    store_data: dict
    emp_data: list[dict]
    team_data: list[dict]

    def __init__(self) -> None:
        """Initialize the dialog and connect UI elements."""
        super().__init__()
        ui_path = resource_path("ui/load_data_manual_dialog.ui")
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
        """Load employee and team data from selected database file."""
        db_path = self.txtDatabasePath.text().strip()
        if not db_path:
            QtWidgets.QMessageBox.warning(self, "Input Required", "Please enter a Database Path.")
            return

        conn = get_db_connection(db_path=db_path)
        if not conn:
            return

        try:
            self.store_data = load_source_store_data(conn=conn)
            self.emp_data = load_source_emp_data(conn=conn)
            self.team_data = load_source_team_data(conn=conn)

            save_local_data(store_data=self.store_data, emp_data=self.emp_data, team_data=self.team_data)

            self.accept()

        except Exception:
            traceback.print_exc()

        finally:
            if conn:
                conn.close()
