"""Main employee hours input window for calculating UPH and generating reports."""
import sys
import os
from typing import cast
from PyQt6 import QtWidgets, QtCore, uic

from utils import resource_path
from utils import generate_accuracy_report
from utils import center_on_screen, apply_style


class EmpSelectWindow(QtWidgets.QMainWindow):
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
        ui_path = resource_path("assets/ui/emp_input_window.ui")
        uic.loadUi(ui_path, self)

        self.store_data = store_data
        self.emp_data = emp_data
        self.zone_data = zone_data

        self.rows_widgets: list[QtWidgets.QWidget] = []
        self.empRowsLayout = cast(QtWidgets.QVBoxLayout, self.scrollAreaWidgetContents.layout())

        for emp in emp_data:
            row = self.create_emp_select_row(emp)
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
        selected_emp_data = []

        for i, row_widget in enumerate(self.rows_widgets):
            checkbox = cast(QtWidgets.QCheckBox, getattr(row_widget, "emp_select"))
            if checkbox.checkState() != QtCore.Qt.CheckState.Checked: continue
            selected_emp_data.append(self.emp_data[i])

        if not self.emp_data:
            QtWidgets.QMessageBox.warning(self, "No Data", "No employee data available to print.")
            return

        generate_accuracy_report(self.store_data, selected_emp_data, self.zone_data, is_aggregate=True)

        self.close()

    @staticmethod
    def get_installed_image_path():
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(__file__)
        return os.path.join(base_dir, "assets", "images", "checkmark.png").replace("\\", "/")

    @staticmethod
    def apply_qss_with_image(widget, qss_file_path, image_path):
        with open(qss_file_path, "r") as f:
            qss = f.read()
        qss = qss.replace("CHECKMARK_IMAGE", image_path.replace("\\", "/"))
        widget.setStyleSheet(qss)

    # TODO: Replace with .ui file
    def create_emp_select_row(self, emp: dict) -> QtWidgets.QWidget:
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

        emp_select = QtWidgets.QCheckBox()
        emp_select.setChecked(True)
        layout.addWidget(emp_select)

        row_widget.setMinimumHeight(40)
        row_widget.emp_select = emp_select
        row_widget.label_id = label_id
        row_widget.label_name = label_name

        qss_file = resource_path("assets/styles/emp_select_row.qss")
        image_path = self.get_installed_image_path()
        self.apply_qss_with_image(row_widget, qss_file, image_path)

        return row_widget
