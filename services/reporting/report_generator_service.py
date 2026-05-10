import logging

from exceptions.report_exceptions import ReportGenerationError
from domain.dto.report_data import StoreReportData, AggregateReportData


class ReportGeneratorService:

    def __init__(self, template_service, data_service, rendering_service, pdf_service):
        self.templates = template_service
        self.data = data_service
        self.renderer = rendering_service
        self.pdf = pdf_service

    def generate_report(self, report_data: StoreReportData):
        try:
            templates = self.templates.get_standard_templates()

            emp_data = self.data.prepare_emp_data(report_data.employees)
            zone_data = self.data.prepare_zone_data(report_data.zones)

            html = self.renderer.render(
                templates=templates,
                store_data=report_data.context,
                emp_data=emp_data,
                zone_data=zone_data,
            )

            self.pdf.export(html)

        except Exception as e:
            logging.exception("Failed to generate report")
            raise ReportGenerationError("Store report generation failed") from e

    def generate_aggregate_report(self, report_data: AggregateReportData):
        try:
            templates = self.templates.get_aggregate_templates()

            emp_data = self.data.prepare_emp_data(report_data.employees)
            zone_data = self.data.prepare_zone_data(report_data.zones)

            html = self.renderer.render(
                templates=templates,
                store_data=report_data.context,
                emp_data=emp_data,
                zone_data=zone_data,
            )

            self.pdf.export(html)

        except Exception as e:
            logging.exception("Failed to generate aggregate report")
            raise ReportGenerationError("Aggregate report generation failed") from e