import sys
import os
from PyQt6 import QtWidgets, uic

DEFAULT_DB_PATH = r"C:\path\to\default\database.accdb"


class ReportDialog(QtWidgets.QDialog):
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("dialog_box.ui", self)
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
        generate_employee_report(db_path=db_path, hours_worked=hours_worked)
        self.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    dialog = ReportDialog()
    dialog.exec()
