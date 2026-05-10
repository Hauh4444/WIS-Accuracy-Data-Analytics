import logging
from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt

from ui.windows.base_window import BaseWindow
from utils.paths import resource_path
from utils.ui import apply_style
from exceptions.database_exceptions import DatabaseConnectionError, DatabaseQueryError
from exceptions.report_exceptions import ReportGenerationError, ReportExportError
from exceptions.wisdom_exceptions import WisdomDataError
from exceptions.validation_exceptions import InvalidHoursError


class EmployeeHoursInputWindow(BaseWindow):

    def _submit(self):
        try:
            self.report_data.employees = self._collect_emp_hours()
            self.controller.generate_current_report(self.report_data)

        except InvalidHoursError as e:
            logging.warning(str(e))
            QtWidgets.QMessageBox.warning(self, "Invalid Input", "One or more employee hours are invalid. Please enter numeric values.")

        except ReportGenerationError:
            QtWidgets.QMessageBox.critical(self, "Report Error", "Failed to generate report.")

        except ReportExportError:
            QtWidgets.QMessageBox.critical(self, "Export Error", "Failed to export PDF report.")

        except DatabaseConnectionError:
            QtWidgets.QMessageBox.critical(self, "Database Error", "Database connection failed.")

        except DatabaseQueryError:
            QtWidgets.QMessageBox.critical(self, "Database Error", "Database query failed.")

        except WisdomDataError:
            QtWidgets.QMessageBox.critical(self, "Data Error", "Failed to load wisdom data.")

        except Exception:
            logging.exception("Unhandled error in EmployeeHoursInputWindow.submit")
            QtWidgets.QMessageBox.critical(self, "Unexpected Error", "An unexpected error occurred.")

        finally:
            self.close()

    def _collect_emp_hours(self):
        updated = []

        for i, row_widget in enumerate(self.rows_widgets):
            txt_hours = row_widget.txt_hours

            raw = txt_hours.text().strip()

            if raw == "":
                hours = 0.0

            else:
                try:
                    hours = float(raw)
                except ValueError as e:
                    raise InvalidHoursError(f"Invalid hours for employee {self.report_data.employees[i].emp_id}") from e

            emp = self.report_data.employees[i]
            emp.hours = hours
            emp.uph = emp.total_qty or 0 / hours if hours > 0 else 0

            updated.append(emp)

        return updated

    def _create_row(self, emp):
        row_widget, layout, label_id, label_name = self._create_base_row(emp)

        txt_hours = QtWidgets.QLineEdit("" if emp.hours is None else str(emp.hours))
        txt_hours.setAlignment(Qt.AlignmentFlag.AlignCenter)
        txt_hours.setFixedWidth(75)
        layout.addWidget(txt_hours)

        def key_handler(event: QtGui.QKeyEvent):
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Down):
                txt_hours.focusNextChild()
            elif event.key() == Qt.Key.Key_Up:
                txt_hours.focusPreviousChild()
            else:
                QtWidgets.QLineEdit.keyPressEvent(txt_hours, event)

        txt_hours.keyPressEvent = key_handler

        row_widget.txt_hours = txt_hours
        row_widget.label_id = label_id
        row_widget.label_name = label_name

        apply_style(row_widget, resource_path("assets/styles/emp_hour_input_row.qss"))

        return row_widget