import logging

from factories.local_connection_factory import LocalConnectionFactory
from services.reporting.report_generator_service import ReportGeneratorService
from services.reporting.report_template_service import ReportTemplateService
from services.reporting.report_data_service import ReportDataService
from services.reporting.report_rendering_service import ReportRenderingService
from services.reporting.pdf_export_service import PdfExportService
from services.local.local_data_save_service import LocalDataSaveService
from repositories.local.local_store_repository import LocalStoreRepository
from repositories.local.local_employee_repository import LocalEmployeeRepository
from repositories.local.local_zone_repository import LocalZoneRepository
from repositories.local.local_discrepancy_repository import LocalDiscrepancyRepository
from repositories.local.local_schema_repository import LocalSchemaRepository
from domain.dto.report_data import StoreReportData, AggregateReportData
from exceptions.report_exceptions import ReportGenerationError
from exceptions.database_exceptions import DatabaseConnectionError, DatabaseQueryError
from exceptions.wisdom_exceptions import WisdomDataError


class EmpReportController:

    def __init__(self):
        self.factory = LocalConnectionFactory()
        self.generator = ReportGeneratorService(
            template_service=ReportTemplateService(),
            data_service=ReportDataService(),
            rendering_service=ReportRenderingService(),
            pdf_service=PdfExportService(),
        )

    def generate_historical_report(self, report_data: StoreReportData):
        try:
            self.generator.generate_report(report_data)

        except (DatabaseConnectionError, DatabaseQueryError, WisdomDataError) as e:
            logging.exception("Historical report data failure")
            raise e

        except Exception as e:
            logging.exception("Unexpected error generating historical report")
            raise ReportGenerationError(str(e)) from e

    def generate_current_report(self, report_data: StoreReportData):
        conn = self.factory.create()

        try:
            store_repo = LocalStoreRepository(conn)
            emp_repo = LocalEmployeeRepository(conn)
            zone_repo = LocalZoneRepository(conn)
            disc_repo = LocalDiscrepancyRepository(conn)
            schema_repo = LocalSchemaRepository(conn)
            save_service = LocalDataSaveService(store_repo, emp_repo, zone_repo, disc_repo, schema_repo)

            self.generator.generate_report(report_data)
            save_service.save_all(report_data)

        except (DatabaseConnectionError, DatabaseQueryError) as e:
            logging.exception("Current report DB failure")
            raise e

        except Exception as e:
            logging.exception("Unexpected error generating current report")
            raise ReportGenerationError(str(e)) from e

        finally:
            conn.close()

    def generate_aggregate_report(self, report_data: AggregateReportData):
        try:
            self.generator.generate_aggregate_report(report_data)

        except (DatabaseConnectionError, DatabaseQueryError, WisdomDataError) as e:
            logging.exception("Aggregate report failure")
            raise e

        except Exception as e:
            logging.exception("Unexpected error generating aggregate report")
            raise ReportGenerationError(str(e)) from e