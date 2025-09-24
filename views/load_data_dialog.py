import os
from PyQt6 import QtWidgets, uic

from services.load_emp_data import load_emp_data
from services.load_team_data import load_team_data
from services.database import get_db_connection
from views.emp_hours_input_window import EmpHoursInputWindow


class LoadDataDialog(QtWidgets.QDialog):
    def __init__(self) -> None:
        super().__init__()
        ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ui", "load_data_dialog.ui"))
        uic.loadUi(ui_path, self)

        self.btnBrowse.clicked.connect(self.browse_database)
        self.btnLoad.clicked.connect(self.on_load_clicked)

        self.center_on_screen()

    def browse_database(self) -> None:
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Database File",
            "",
            "Access Databases (*.mdb *.accdb);;All Files (*)"
        )
        if file_path:
            self.txtDatabasePath.setText(file_path)

    def center_on_screen(self) -> None:
        screen = QtWidgets.QApplication.primaryScreen()
        if not screen:
            return
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def on_load_clicked(self) -> None:
        db_path = self.txtDatabasePath.text().strip()

        conn = get_db_connection(db_path=db_path)
        if not conn:
            return

        try:
            emp_data = load_emp_data(conn=conn)
            team_data = load_team_data(conn=conn)

            window = EmpHoursInputWindow(emp_data, team_data)
            window.show()

            self.accept()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Load Error",
                f"An error occurred while loading data:\n{e}"
            )