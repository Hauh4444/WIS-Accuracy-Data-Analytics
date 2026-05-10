import logging
from typing import cast
from PyQt6 import QtWidgets, QtCore

from ui.windows.base_window import BaseWindow
from domain.dto.report_data import AggregateReportData
from utils.paths import resource_path, get_installed_image_path
from utils.ui import apply_qss_with_image
from exceptions.report_exceptions import ReportGenerationError
from exceptions.validation_exceptions import MissingEmployeeDataError


class EmployeeSelectWindow(BaseWindow):

    def _submit(self):
        try:
            selected_emp_data = []

            for i, row_widget in enumerate(self.rows_widgets):
                checkbox = cast(QtWidgets.QCheckBox, getattr(row_widget, "emp_select"))

                if checkbox.checkState() != QtCore.Qt.CheckState.Checked:
                    continue

                selected_emp_data.append(self.report_data.employees[i])

            if not selected_emp_data:
                raise MissingEmployeeDataError("No employee selected")

            filtered_report = AggregateReportData(context=self.report_data.context, employees=selected_emp_data, zones=self.report_data.zones,)

            self.controller.generate_aggregate_report(filtered_report)

        except MissingEmployeeDataError:
            QtWidgets.QMessageBox.warning(self, "No Selection", "Select at least one employee.")
            return

        except ReportGenerationError:
            QtWidgets.QMessageBox.critical(self, "Report Error", "Failed to generate report.")

        except Exception:
            logging.exception("Unhandled error in EmployeeSelectWindow")
            QtWidgets.QMessageBox.critical(self, "Unexpected Error", "Failed to generate report.")

        finally:
            self.close()

    def _create_row(self, emp):
        row_widget, layout, label_id, label_name = self._create_base_row(emp)

        emp_select = QtWidgets.QCheckBox()
        emp_select.setChecked(True)
        layout.addWidget(emp_select)

        row_widget.emp_select = emp_select
        row_widget.label_id = label_id
        row_widget.label_name = label_name

        qss_file = resource_path("assets/styles/emp_select_row.qss")
        image_path = get_installed_image_path()
        apply_qss_with_image(row_widget, qss_file, image_path)

        return row_widget