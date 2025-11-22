"""Dynamic database loading dialog using WISDOM job number convention."""
import traceback
import pyodbc
from PyQt6 import QtWidgets, uic

from database.connection import get_storage_db_connection
from utils.paths import resource_path
from utils.ui_utils import center_on_screen
from services import load_local_store_data, load_local_emp_data, load_local_team_data


class LoadLocalDataDialog(QtWidgets.QDialog):
    """Dialog for loading database using job number input."""
    txtJobNumber: QtWidgets.QLineEdit
    btnLoad: QtWidgets.QPushButton

    store_data: dict
    emp_data: list[dict]
    team_data: list[dict]

    def __init__(self) -> None:
        """Initialize the dialog and connect UI elements."""
        super().__init__()
        ui_path = resource_path("ui/load_local_data_dialog.ui")
        uic.loadUi(ui_path, self)

        self.btnLoad.clicked.connect(self.load_database)

        center_on_screen(widget=self)

    def load_database(self) -> None:
        """Load database using WISDOM path convention: C:\\WISDOM\\JOBS\\{job_number}\\11355\\{job_number}.MDB"""
        job_number = self.txtJobNumber.text().strip()
        if not job_number:
            QtWidgets.QMessageBox.warning(self, "Input Required", "Please enter a Job Number.")
            return

        conn = get_storage_db_connection()
        if not conn:
            self.reject()
            return

        try:
            self.store_data = load_local_store_data(conn=conn, store=job_number)
            self.emp_data = load_local_emp_data(conn=conn, store=job_number)
            self.team_data = load_local_team_data(conn=conn, store=job_number)

            self.accept()

        except:
            traceback.print_exc()
            self.reject()

        finally:
            if conn:
                conn.close()

    def get_data(self):
        return self.store_data, self.emp_data, self.team_data