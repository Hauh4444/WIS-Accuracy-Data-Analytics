import logging
from PyQt6 import QtWidgets

from ui.dialogs.stats_source_dialog import StatsSourceDialog
from ui.dialogs.load_local_data_dialog import LoadLocalDataDialog
from ui.dialogs.load_wisdom_data_dynamic_dialog import LoadWisdomDataDynamicDialog
from ui.dialogs.load_wisdom_data_manual_dialog import LoadWisdomDataManualDialog
from ui.dialogs.load_aggregate_data_dialog import LoadAggregateDataDialog
from ui.windows.employee_hours_input_window import EmployeeHoursInputWindow
from ui.windows.employee_select_window import EmployeeSelectWindow
from domain.enums.stats_source import StatsSource
from exceptions.database_exceptions import DatabaseConnectionError, DatabaseQueryError
from exceptions.report_exceptions import ReportGenerationError, ReportExportError
from exceptions.validation_exceptions import ValidationError
from exceptions.wisdom_exceptions import WisdomDataError


class ApplicationController:

    def __init__(self, container):
        self.container = container
        self.window = None

    def run(self):
        try:
            source_dialog = StatsSourceDialog()

            if not source_dialog.exec():
                return

            source = source_dialog.selected_source

            if source == StatsSource.HISTORICAL:
                self.run_historical()

            elif source == StatsSource.CURRENT:
                self.run_current()

            elif source == StatsSource.AGGREGATE:
                self.run_aggregate()

        except ValidationError as e:
            logging.warning(str(e))
            QtWidgets.QMessageBox.warning(None, "Validation Error", str(e))

        except DatabaseConnectionError:
            QtWidgets.QMessageBox.critical(None, "Database Error", "Database connection failed.")

        except DatabaseQueryError:
            QtWidgets.QMessageBox.critical(None, "Database Error", "Database query failed.")

        except WisdomDataError:
            QtWidgets.QMessageBox.critical(None, "Wisdom Error", "Failed to load wisdom data.")

        except ReportGenerationError:
            QtWidgets.QMessageBox.critical(None, "Report Error", "Failed to generate report.")

        except ReportExportError:
            QtWidgets.QMessageBox.critical(None, "Export Error", "Failed to export report.")

        except Exception:
            logging.exception("Unhandled error in ApplicationController.run")
            QtWidgets.QMessageBox.critical(None, "Unexpected Error", "An unexpected error occurred.")

    def run_historical(self):
        controller = self.container.local_store_data_controller()
        dialog = LoadLocalDataDialog(controller)

        if not dialog.exec():
            return

        data = dialog.result_data

        controller = self.container.emp_report_controller()

        controller.generate_historical_report(data)

    def run_current(self):
        controller = self.container.source_data_controller()
        generator = self.container.emp_report_controller()
        dialog = LoadWisdomDataDynamicDialog(controller)

        if not dialog.exec():
            dialog = LoadWisdomDataManualDialog(controller)

            if not dialog.exec():
                return

        data = dialog.result_data

        self.window = EmployeeHoursInputWindow(data, generator)
        self.window.show()

    def run_aggregate(self):
        controller = self.container.aggregate_data_controller()
        generator = self.container.emp_report_controller()
        dialog = LoadAggregateDataDialog(controller)

        if not dialog.exec():
            return

        data = dialog.result_data

        self.window = EmployeeSelectWindow(data, generator)
        self.window.show()