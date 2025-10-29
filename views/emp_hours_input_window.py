"""Main employee hours input window for calculating UPH and generating reports."""
import os
from typing import cast

from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt

from utils.report_generator import generate_accuracy_report
from utils.paths import resource_path


class EmpHoursInputWindow(QtWidgets.QMainWindow):
    """Main window for employee hours input and report generation."""
    scrollArea: QtWidgets.QScrollArea
    scrollAreaWidgetContents: QtWidgets.QWidget
    empRowsLayout: QtWidgets.QVBoxLayout
    btnPrint: QtWidgets.QPushButton

    def __init__(self, store_data: dict, emp_data: list[dict], team_data: list[dict]):
        """Initialize the window with employee and team data.
        
        Args:
            store_data: Dictionary containing store data
            emp_data: List of employee data dictionaries
            team_data: List of team data dictionaries
        """
        super().__init__()
        ui_path = resource_path("ui/emp_hours_window.ui")
        uic.loadUi(ui_path, self)

        self.emp_row_qss_path = resource_path("styles/emp_hour_input_row.qss")
        self.scrollbar_qss_path = resource_path("styles/scrollbar.qss")

        self.store_data = store_data
        self.emp_data = emp_data
        self.team_data = team_data

        self.rows_widgets: list[QtWidgets.QWidget] = []
        self.empRowsLayout = cast(QtWidgets.QVBoxLayout, self.scrollAreaWidgetContents.layout())

        for emp in emp_data:
            row = self.create_emp_hour_input_row(emp=emp)
            self.empRowsLayout.addWidget(row)
            self.rows_widgets.append(row)

        self.empRowsLayout.addStretch()
        self.apply_scrollbar_style()
        self.resize(600, 600)
        self.center_on_screen()
        self.btnPrint.clicked.connect(self.print_report)


    def create_emp_hour_input_row(self, emp: dict) -> QtWidgets.QWidget:
        """Create a widget row for employee data input.
        
        Args:
        Args:
            emp: Employee data dictionary
            
        Returns:
            Widget containing employee ID, name, and hours input field
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

        self.apply_emp_hour_input_row_style(row=row_widget)
        return row_widget


    def apply_emp_hour_input_row_style(self, row: QtWidgets.QWidget) -> None:
        """Apply stylesheet to employee row widget."""
        if os.path.exists(self.emp_row_qss_path):
            with open(self.emp_row_qss_path, "r") as f:
                row.setStyleSheet(f.read())
        else:
            print(f"Warning: Employee hour input row style file not found at {self.emp_row_qss_path}")


    def apply_scrollbar_style(self) -> None:
        """Apply stylesheet to the scroll area."""
        if os.path.exists(self.scrollbar_qss_path):
            with open(self.scrollbar_qss_path, "r") as f:
                self.scrollArea.setStyleSheet(f.read())
        else:
            print(f"Warning: Scrollbar style file not found at {self.scrollbar_qss_path}")


    def center_on_screen(self) -> None:
        """Center the window on the primary screen."""
        screen = QtWidgets.QApplication.primaryScreen()
        if not screen:
            return
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)


    def print_report(self) -> None:
        """Process hours input and generate accuracy report."""
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
        
        generate_accuracy_report(store_data=self.store_data, emp_data=self.emp_data, team_data=self.team_data)
        self.close()
