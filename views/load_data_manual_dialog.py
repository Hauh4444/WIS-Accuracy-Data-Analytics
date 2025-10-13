"""Manual database loading dialog with file browser."""
import traceback
from PyQt6 import QtWidgets, uic

from services.database import get_db_connection
from services.resource_utils import resource_path
from services.load_store_data import load_store_data
from services.load_emp_data import load_emp_data
from services.load_team_data import load_team_data


class LoadDataManualDialog(QtWidgets.QDialog):
    """Dialog for loading database using file browser."""
    
    def __init__(self) -> None:
        """Initialize the dialog and connect UI elements."""
        super().__init__()
        ui_path = resource_path("ui/load_data_manual_dialog.ui")
        uic.loadUi(ui_path, self)
        self.btnBrowse.clicked.connect(self.browse_database)
        self.btnLoad.clicked.connect(self.load_database)
        self.center_on_screen()


    def center_on_screen(self) -> None:
        """Center the dialog on the primary screen."""
        screen = QtWidgets.QApplication.primaryScreen()
        if not screen:
            return
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)


    def browse_database(self) -> None:
        """Open file dialog to select database file."""
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 
            "Select Database File", 
            "", 
            "Access Databases (*.mdb *.accdb);;All Files (*)"
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
            self.store_data = load_store_data(conn=conn)
            self.emp_data = load_emp_data(conn=conn)
            self.team_data = load_team_data(conn=conn)
            self.accept()
        except Exception:
            traceback.print_exc()        
        finally:
            if conn:
                conn.close()
