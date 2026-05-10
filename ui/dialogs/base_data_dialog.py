from PyQt6 import QtWidgets

from domain.dto.report_data import StoreReportData, AggregateReportData


class BaseDataDialog(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        self.result_data: StoreReportData | AggregateReportData | None = None

    def _set_result_data(self, data: StoreReportData | AggregateReportData):
        self.result_data = data