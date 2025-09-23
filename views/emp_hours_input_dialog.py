import os
from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import Qt

from services.report_generator import generate_employee_report


def create_employee_row(emp: dict) -> QtWidgets.QWidget:
    row_widget = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout(row_widget)
    layout.setContentsMargins(5, 5, 5, 5)
    layout.setSpacing(10)

    label_id = QtWidgets.QLabel(str(emp.get("employee_id", "")))
    label_id.setFixedWidth(120)
    layout.addWidget(label_id)

    label_name = QtWidgets.QLabel(emp.get("employee_name", ""))
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
    return row_widget


class EmpHoursInputWindow(QtWidgets.QMainWindow):
    def __init__(self, emp_data: list[dict], team_data: list[dict]):
        super().__init__()
        ui_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ui", "emp_hours_window.ui"))
        uic.loadUi(ui_path, self)

        self.emp_data = emp_data
        self.team_data = team_data
        self.rows_widgets: list[QtWidgets.QWidget] = []
        self.empRowsLayout = self.scrollAreaWidgetContents.layout()

        for emp in emp_data:
            row = create_employee_row(emp)
            row.setStyleSheet(self.scrollAreaWidgetContents.styleSheet())
            self.empRowsLayout.addWidget(row)
            self.rows_widgets.append(row)

        self.empRowsLayout.addStretch()
        self.apply_scrollbar_style()

        self.btnPrint.clicked.connect(self.on_print_clicked)

        self.resize(600, 600)
        self.center_on_screen()

    def apply_scrollbar_style(self) -> None:
        scrollbar_qss_path = "styles/scrollbar.qss"
        if os.path.exists(scrollbar_qss_path):
            with open(scrollbar_qss_path, "r") as f:
                self.scrollArea.setStyleSheet(f.read())
        else:
            print(f"Warning: Scrollbar style file not found at {scrollbar_qss_path}")

    def center_on_screen(self) -> None:
        screen = QtWidgets.QApplication.primaryScreen()
        if not screen:
            return
        screen_geometry = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def on_print_clicked(self) -> None:
        for i, row_widget in enumerate(self.rows_widgets):
            hours_text = row_widget.txt_hours.text().strip()
            emp_hours = float(hours_text) if hours_text.replace(".", "", 1).isdigit() else 0.0

            self.emp_data[i]["hours"] = emp_hours
            if emp_hours > 0:
                self.emp_data[i]["uph"] = self.emp_data[i]["total_quantity"] / emp_hours
            else:
                self.emp_data[i]["uph"] = 0

        if not self.emp_data:
            QtWidgets.QMessageBox.warning(self, "No Data", "No employee data available to print.")
            return

        generate_employee_report(self.emp_data, self.team_data)
        QtWidgets.QMessageBox.information(self, "Report", "Employee report generated successfully.")
        self.close()
