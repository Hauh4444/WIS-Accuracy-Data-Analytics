"""Dynamic database loading dialog using WISDOM job number convention."""
from PyQt6 import QtWidgets, uic

from database import get_db_connection
from utils import resource_path
from utils import center_on_screen
from services import load_source_store_data, load_source_emp_data, load_source_zone_data


class LoadSourceDataDynamicDialog(QtWidgets.QDialog):
    """Dialog for loading database using job number input."""
    txtJobNumber: QtWidgets.QLineEdit
    btnLoad: QtWidgets.QPushButton

    store_data: dict
    emp_data: list[dict]
    zone_data: list[dict]
    
    def __init__(self) -> None:
        """Initialize the dialog and connect UI elements."""
        super().__init__()
        ui_path = resource_path("assets/ui/load_source_data_dynamic_dialog.ui")
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

        conn = get_db_connection(db_path)
        if not conn:
            self.reject()
            return

        self.store_data = load_source_store_data(conn)
        self.emp_data = load_source_emp_data(conn)
        self.zone_data = load_source_zone_data(conn)

        conn.close()
        self.accept()