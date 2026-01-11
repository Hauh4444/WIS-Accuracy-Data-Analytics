import tempfile
import webbrowser
import logging
from io import BytesIO
from pathlib import Path
from PyQt6 import QtWidgets
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader

from utils import resource_path


def generate_accuracy_report(store_data: dict, emp_data: list[dict], zone_data: list[dict], is_date_range: bool = False) -> None:
    """Generate and display accuracy reports for employees and zones.
    
    Args:
        store_data: Dictionary containing store data
        emp_data: List of employee data dictionaries
        zone_data: List of zone data dictionaries
        is_date_range: If True, generates date_range report. Otherwise, generates standard store report.
    
    Raises:
        ValueError: Invalid or missing input data
        RuntimeError: Missing templates or PDF generation failure
    """
    try:
        if not store_data:
            raise ValueError("store_data cannot be empty or None")
        if not isinstance(emp_data, list) or not isinstance(zone_data, list):
            raise ValueError("emp_data and zone_data must be lists")

        templates_path = resource_path("assets/templates")
        if not templates_path or not Path(templates_path).exists():
            raise RuntimeError("Templates directory not found or invalid")

        env = Environment(loader=FileSystemLoader(templates_path))

        if is_date_range:
            template_files = ["date_range_emp_report.html", "date_range_zone_report.html"]
        else:
            template_files = ["emp_report.html", "zone_report.html", "disc_report.html"]

        for template in template_files:
            if not Path(resource_path(f"assets/templates/{template}")).exists():
                raise RuntimeError(f"Required template file not found: {template}")

        templates = [env.get_template(t) for t in template_files]

        sorted_emp_data = sorted(emp_data, key=lambda x: (-x["uph"], -x["total_quantity"]))
        sorted_zone_data = sorted(zone_data, key=lambda x: x["zone_id"])

        if is_date_range:
            html_fragments = [
                templates[0].render(page_headers=store_data, emp_data=sorted_emp_data),
                templates[1].render(page_headers=store_data, zone_data=sorted_zone_data),
            ]
        else:
            html_fragments = [
                templates[0].render(page_headers=store_data, emp_data=sorted_emp_data),
                templates[1].render(page_headers=store_data, zone_data=sorted_zone_data),
                templates[2].render(page_headers=store_data, emp_data=sorted_emp_data),
            ]

        full_html = ""
        for i, html in enumerate(html_fragments):
            if i > 0:
                full_html += "<div style='page-break-before: always;'></div>"
            full_html += html

        pdf_buffer = BytesIO()
        result = pisa.CreatePDF(full_html, pdf_buffer)
        if result.err:
            raise RuntimeError("PDF generation failed - xhtml2pdf encountered an error")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_buffer.getvalue())
            tmp_file.flush()
            pdf_path = Path(tmp_file.name).resolve()
            if not pdf_path.exists():
                raise RuntimeError("Failed to create temporary PDF file")
            webbrowser.open(f"file://{pdf_path}")

    except ValueError as e:
        logging.exception("Data validation error while generating accuracy report")
        QtWidgets.QMessageBox.warning(
            None,
            "Data Validation Error",
            f"Invalid or missing input data while preparing the accuracy report.\n\nDetails:\n{str(e)}"
        )
        raise

    except RuntimeError as e:
        logging.exception("Report generation error while generating accuracy report")
        QtWidgets.QMessageBox.warning(
            None,
            "Report Generation Error",
            f"Failed to generate the accuracy report due to missing templates or PDF generation issues.\n\nDetails:\n{str(e)}"
        )
        raise

    except Exception as e:
        logging.exception("Unhandled error while generating accuracy report")
        QtWidgets.QMessageBox.warning(
            None,
            "Unexpected Error",
            f"An unexpected failure occurred during accuracy report generation.\n\nDetails:\n{str(e)}"
        )
        raise
