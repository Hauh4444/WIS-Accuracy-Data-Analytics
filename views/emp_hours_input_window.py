"""Main employee hours input window for calculating UPH and generating reports."""
from typing import cast
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt

from services import save_local_data
from database import get_storage_db_connection
from utils import resource_path
from utils import generate_accuracy_report
from utils import center_on_screen, apply_style


# TODO: Change to QtDialog
class EmpHoursInputWindow(QtWidgets.QMainWindow):
    """Main window for employee hours input and report generation."""
    scrollArea: QtWidgets.QScrollArea
    scrollAreaWidgetContents: QtWidgets.QWidget
    empRowsLayout: QtWidgets.QVBoxLayout
    btnPrint: QtWidgets.QPushButton

    def __init__(self, store_data: dict, emp_data: list[dict], zone_data: list[dict]) -> None:
        """Initialize the window with employee and zone data.
        
        Args:
            store_data: Dictionary containing store data
            emp_data: List of employee data dictionaries
            zone_data: List of zone data dictionaries
        """
        super().__init__()
        ui_path = resource_path("assets/ui/emp_hours_window.ui")
        uic.loadUi(ui_path, self)

        self.store_data = store_data
        self.emp_data = emp_data
        self.zone_data = zone_data

        self.rows_widgets: list[QtWidgets.QWidget] = []
        self.empRowsLayout = cast(QtWidgets.QVBoxLayout, self.scrollAreaWidgetContents.layout())

        for emp in emp_data:
            # TODO: Replace with .ui file
            row = self.create_emp_hour_input_row(emp)
            self.empRowsLayout.addWidget(row)
            self.rows_widgets.append(row)

        self.empRowsLayout.addStretch()
        self.btnPrint.clicked.connect(self.print_report)

        self.setWindowTitle("WIS Accuracy Data Analytics")
        self.show()
        self.raise_()
        self.activateWindow()
        self.resize(600, 600)

        # TODO: Probably a way to not have to do this
        apply_style(widget=self.scrollArea, style_path=resource_path("assets/styles/scrollbar.qss"))
        center_on_screen(widget=self)

    def print_report(self) -> None:
        """Process hours inputs and generate accuracy report."""
        for i, row_widget in enumerate(self.rows_widgets):
            txt_hours = cast(QtWidgets.QLineEdit, getattr(row_widget, "txt_hours"))
            hours_text = txt_hours.text().strip()
            emp_hours = float(hours_text) if hours_text.replace(".", "", 1).isdigit() else 0.0
            self.emp_data[i]["hours"] = emp_hours
            if emp_hours > 0:
                self.emp_data[i]["uph"] = self.emp_data[i]["total_quantity"] / emp_hours
            else:
                self.emp_data[i]["uph"] = 0
        
        if not self.emp_data:
            QtWidgets.QMessageBox.warning(self, "No Data", "No employee data available to print.")
            return

        conn = get_storage_db_connection()
        if not conn:
            self.close()
            return

        save_local_data(conn, self.store_data, self.emp_data, self.zone_data)
        generate_accuracy_report(self.store_data, self.emp_data, self.zone_data, season=False)

        conn.close()
        self.close()

    @staticmethod
    def create_emp_hour_input_row(emp: dict) -> QtWidgets.QWidget:
        """Create a widget row for employee data input.

        Args:
            emp: Employee data dictionary

        Returns:
            Row widget containing employee ID, name, and hours input field
        """
        row_widget = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(row_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        label_id = QtWidgets.QLabel(emp.get("emp_number", ""))
        label_id.setFixedWidth(120)
        layout.addWidget(label_id)

        label_name = QtWidgets.QLabel(emp.get("emp_name", ""))
        label_name.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        layout.addWidget(label_name)

        txt_hours = QtWidgets.QLineEdit(str(emp.get("hours", "")))
        txt_hours.setAlignment(Qt.AlignmentFlag.AlignCenter)
        txt_hours.setFixedWidth(75)
        layout.addWidget(txt_hours)
        txt_hours.returnPressed.connect(lambda: txt_hours.focusNextChild())

        row_widget.setMinimumHeight(40)
        row_widget.txt_hours = txt_hours
        row_widget.label_id = label_id
        row_widget.label_name = label_name

        apply_style(widget=row_widget, style_path=resource_path("assets/styles/emp_hour_input_row.qss"))
        return row_widget
