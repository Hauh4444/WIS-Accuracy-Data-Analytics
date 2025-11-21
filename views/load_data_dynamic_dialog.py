"""Dynamic database loading dialog using WISDOM job number convention."""
import traceback
from PyQt6 import QtWidgets, uic

from database.connection import get_db_connection
from utils.paths import resource_path
from utils.ui_utils import center_on_screen
from services.load_source_store_data import load_source_store_data
from services.load_source_emp_data import load_source_emp_data
from services.load_source_team_data import load_source_team_data
from services.save_local_data import save_local_data


class LoadDataDynamicDialog(QtWidgets.QDialog):
    """Dialog for loading database using job number input."""
    txtJobNumber: QtWidgets.QLineEdit
    btnLoad: QtWidgets.QPushButton

    store_data: dict
    emp_data: list[dict]
    team_data: list[dict]
    
    def __init__(self) -> None:
        """Initialize the dialog and connect UI elements."""
        super().__init__()
        ui_path = resource_path("ui/load_data_dynamic_dialog.ui")
        uic.loadUi(ui_path, self)

        self.btnLoad.clicked.connect(self.load_database)

        center_on_screen(widget=self)

    def load_database(self) -> None:
        """Load database using WISDOM path convention: C:\\WISDOM\\JOBS\\{job_number}\\11355\\{job_number}.MDB"""
        job_number = self.txtJobNumber.text().strip()
        if not job_number:
            QtWidgets.QMessageBox.warning(self, "Input Required", "Please enter a Job Number.")
            return
        
        db_path = rf"C:\WISDOM\JOBS\{job_number}\11355\{job_number}.MDB"
        conn = get_db_connection(db_path=db_path)
        if not conn:
            self.reject()
            return

        try:
            self.store_data = load_source_store_data(conn=conn)
            self.emp_data = load_source_emp_data(conn=conn)
            self.team_data = load_source_team_data(conn=conn)

            save_local_data(store_data=self.store_data, emp_data=self.emp_data, team_data=self.team_data)

            self.accept()

        except Exception:
            traceback.print_exc()
            self.reject()

        finally:
            if conn:
                conn.close()
