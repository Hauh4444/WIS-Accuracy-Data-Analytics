from controllers.local_store_data_controller import LocalStoreDataController
from controllers.wisdom_data_controller import WisdomDataController
from controllers.local_aggregate_data_controller import LocalAggregateDataController
from controllers.employee_report_controller import EmpReportController


class AppContainer:

    @staticmethod
    def local_store_data_controller():
        return LocalStoreDataController()

    @staticmethod
    def source_data_controller():
        return WisdomDataController()

    @staticmethod
    def aggregate_data_controller():
        return LocalAggregateDataController()

    @staticmethod
    def emp_report_controller():
        return EmpReportController()