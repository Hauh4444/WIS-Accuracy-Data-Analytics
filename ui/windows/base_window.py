from abc import abstractmethod
from typing import cast
from PyQt6 import QtWidgets, uic

from controllers.employee_report_controller import EmpReportController
from domain.dto.report_data import StoreReportData, AggregateReportData
from utils.ui import center_on_screen, apply_style
from utils.paths import resource_path


class BaseWindow(QtWidgets.QMainWindow):

    def __init__(self, report_data: StoreReportData | AggregateReportData, controller: EmpReportController):
        super().__init__()

        ui_path = resource_path("assets/ui/window.ui")
        uic.loadUi(ui_path, self)

        self.report_data = report_data
        self.controller = controller

        self.rows_widgets: list[QtWidgets.QWidget] = []

        self.empRowsLayout = cast(QtWidgets.QVBoxLayout, self.scrollAreaWidgetContents.layout())

        for emp in self.report_data.employees:
            row = self._create_row(emp)

            self.empRowsLayout.addWidget(row)
            self.rows_widgets.append(row)

        self.empRowsLayout.addStretch()

        self.btnPrint.clicked.connect(self._submit)

        self.setWindowTitle("WIS Accuracy Data Analytics")
        self.resize(600, 600)

        apply_style(self.scrollArea, resource_path("assets/styles/scrollbar.qss"))
        center_on_screen(self)

    @abstractmethod
    def _submit(self):
        pass

    @abstractmethod
    def _create_row(self, emp):
        pass

    @staticmethod
    def _create_base_row(emp) -> tuple[QtWidgets.QWidget, QtWidgets.QHBoxLayout, QtWidgets.QLabel, QtWidgets.QLabel]:
        row_widget = QtWidgets.QWidget()

        layout = QtWidgets.QHBoxLayout(row_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        label_id = QtWidgets.QLabel(emp.emp_id)
        label_id.setFixedWidth(120)
        layout.addWidget(label_id)

        label_name = QtWidgets.QLabel(emp.emp_name)
        label_name.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Fixed
        )
        layout.addWidget(label_name)

        row_widget.setMinimumHeight(40)

        return row_widget, layout, label_id, label_name