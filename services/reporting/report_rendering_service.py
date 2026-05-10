import logging

from exceptions.report_exceptions import ReportGenerationError


class ReportRenderingService:

    @staticmethod
    def render(templates, store_data, emp_data, zone_data):
        try:
            html_fragments = []

            for template in templates:
                html_fragments.append(template.render(store_data=store_data, emp_data=emp_data, zone_data=zone_data))

            return "<div style='page-break-before: always;'></div>".join(html_fragments)

        except Exception as e:
            logging.exception("Failed to render report templates")
            raise ReportGenerationError("Report rendering failed") from e