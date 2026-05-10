import logging

from factories.wisdom_connection_factory import WisdomConnectionFactory
from mappers.wisdom.wisdom_store_mapper import WisdomStoreMapper
from mappers.wisdom.wisdom_employee_mapper import WisdomEmployeeMapper
from mappers.wisdom.wisdom_zone_mapper import WisdomZoneMapper
from services.wisdom.wisdom_store_service import WisdomStoreService
from services.wisdom.wisdom_employee_service import WisdomEmployeeService
from services.wisdom.wisdom_zone_service import WisdomZoneService
from repositories.wisdom.wisdom_store_repository import WisdomStoreRepository
from repositories.wisdom.wisdom_employee_repository import WisdomEmployeeRepository
from repositories.wisdom.wisdom_zone_repository import WisdomZoneRepository
from utils.paths import build_wisdom_db_path
from domain.dto.report_data import StoreReportData
from exceptions.database_exceptions import DatabaseConnectionError, DatabaseQueryError
from exceptions.wisdom_exceptions import WisdomDataError
from exceptions.report_exceptions import ReportGenerationError


class WisdomDataController:

    def load_from_job_number(self, job_number: str) -> StoreReportData | None:
        return self._load(build_wisdom_db_path(job_number))

    def load_from_path(self, db_path: str) -> StoreReportData | None:
        return self._load(db_path)

    @staticmethod
    def _load(db_path: str) -> StoreReportData | None:
        factory = WisdomConnectionFactory(db_path)
        conn = factory.create()

        try:
            store_repo = WisdomStoreRepository(conn)
            emp_repo = WisdomEmployeeRepository(conn)
            zone_repo = WisdomZoneRepository(conn)

            store_mapper = WisdomStoreMapper()
            emp_mapper = WisdomEmployeeMapper()
            zone_mapper = WisdomZoneMapper()

            store_service = WisdomStoreService(store_repo, store_mapper)
            emp_service = WisdomEmployeeService(emp_repo, emp_mapper)
            zone_service = WisdomZoneService(zone_repo, zone_mapper)

            context=store_service.fetch_store_data()
            employees=emp_service.fetch_employee_data()
            zones=zone_service.fetch_zone_data()

            return StoreReportData(context, employees, zones)

        except (DatabaseConnectionError, DatabaseQueryError, WisdomDataError) as e:
            logging.exception("Wisdom data load failure")
            raise e

        except Exception as e:
            logging.exception("Unexpected wisdom data load error")
            raise ReportGenerationError(str(e)) from e

        finally:
            conn.close()
