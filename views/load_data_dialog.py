import os
from PyQt6 import QtWidgets, uic

from services.load_data import load_data

DEFAULT_DB_PATH = r"C:\path\to\default\database.accdb"

class ReportDialog(QtWidgets.QDialog):
    def __init__(self) -> None:
        super().__init__()
        ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ui", "dialog_box.ui"))
        uic.loadUi(ui_path, self)
        self.btnBrowse.clicked.connect(self.browse_database)
        ok_button = self.buttonBox.button(QtWidgets.QDialogButtonBox.StandardButton.Ok)
        ok_button.clicked.connect(self.on_ok_clicked)
        self.buttonBox.accepted.disconnect()

    def browse_database(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Database File",
            "",
            "Access Databases (*.mdb *.accdb);;All Files (*)"
        )
        if file_path:
            self.txtDatabasePath.setText(file_path)

    def on_ok_clicked(self) -> None:
        db_path = self.txtDatabasePath.text().strip() or DEFAULT_DB_PATH
        hours_text = self.txtHours.text().strip()
        if not hours_text:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter the number of hours.")
            return
        if not os.path.exists(db_path):
            QtWidgets.QMessageBox.warning(self, "Input Error", f"Database file not found: {db_path}")
            return
        try:
            hours_worked = float(hours_text)
        except ValueError:
            QtWidgets.QMessageBox.warning(self, "Input Error", "Please enter a valid number for hours.")
            return
        load_data(db_path=db_path)
        self.accept()