import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from utils.paths import resource_path
from exceptions.report_exceptions import ReportGenerationError
from exceptions.file_exceptions import FileLoadError, InvalidFileFormatError


class ReportTemplateService:

    def __init__(self):
        try:
            path = resource_path("assets/templates")

            if not path or not Path(path).exists():
                raise FileLoadError(f"Template directory not found: {path}")

            self.env = Environment(loader=FileSystemLoader(path))

        except FileLoadError:
            raise

        except Exception as e:
            logging.exception("Failed to initialize ReportTemplateService")
            raise ReportGenerationError("Failed to initialize templates") from e

    def get_standard_templates(self):
        try:
            return [
                self.env.get_template("emp_report.html"),
                self.env.get_template("emp_man_report.html"),
                self.env.get_template("zone_report.html"),
                self.env.get_template("disc_report.html"),
                self.env.get_template("man_report.html"),
            ]

        except TemplateNotFound as e:
            logging.exception("Missing standard report template")
            raise InvalidFileFormatError("Standard report template missing or invalid") from e

        except Exception as e:
            logging.exception("Unexpected error loading standard templates")
            raise ReportGenerationError("Failed to load standard templates") from e

    def get_aggregate_templates(self):
        try:
            return [
                self.env.get_template("aggregate_emp_report.html"),
                self.env.get_template("aggregate_zone_report.html"),
            ]

        except TemplateNotFound as e:
            logging.exception("Missing aggregate report template")
            raise InvalidFileFormatError("Aggregate report template missing or invalid") from e

        except Exception as e:
            logging.exception("Unexpected error loading aggregate templates")
            raise ReportGenerationError("Failed to load aggregate templates") from e