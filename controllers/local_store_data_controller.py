import logging

from factories.local_connection_factory import LocalConnectionFactory
from mappers.local.local_report_context_mapper import LocalReportContextMapper
from mappers.local.local_employee_mapper import LocalEmployeeMapper
from mappers.local.local_zone_mapper import LocalZoneMapper
from services.local.local_store_service import LocalStoreService
from services.local.local_employee_service import LocalEmployeeService
from services.local.local_zone_service import LocalZoneService
from repositories.local.local_store_repository import LocalStoreRepository
from repositories.local.local_employee_repository import LocalEmployeeRepository
from repositories.local.local_discrepancy_repository import LocalDiscrepancyRepository
from repositories.local.local_zone_repository import LocalZoneRepository
from domain.dto.report_data import StoreReportData
from exceptions.database_exceptions import DatabaseConnectionError, DatabaseQueryError
from exceptions.wisdom_exceptions import WisdomDataError
from exceptions.report_exceptions import ReportGenerationError


class LocalStoreDataController:

    def __init__(self):
        self.factory = LocalConnectionFactory()

    def load(self, store_number) -> StoreReportData | None:
        conn = self.factory.create()

        try:
            store_repo = LocalStoreRepository(conn)
            emp_repo = LocalEmployeeRepository(conn)
            zone_err_repo = LocalDiscrepancyRepository(conn)
            zone_repo = LocalZoneRepository(conn)

            store_mapper = LocalReportContextMapper()
            emp_mapper = LocalEmployeeMapper()
            zone_mapper = LocalZoneMapper()

            store_service = LocalStoreService(store_repo, store_mapper)
            emp_service = LocalEmployeeService(emp_repo, zone_err_repo, emp_mapper)
            zone_service = LocalZoneService(zone_repo, zone_mapper)

            context = store_service.fetch_store_data(store_number)
            employees = emp_service.fetch_employee_data(store_number)
            zones = zone_service.fetch_zone_data(store_number)

            return StoreReportData(context, employees, zones)

        except (DatabaseConnectionError, DatabaseQueryError, WisdomDataError) as e:
            logging.exception("Store data load failure")
            raise e

        except Exception as e:
            logging.exception("Unexpected store data load error")
            raise ReportGenerationError(str(e)) from e

        finally:
            conn.close()