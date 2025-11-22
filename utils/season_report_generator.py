"""PDF report generator using Jinja2 templates and xhtml2pdf."""
import tempfile
import webbrowser
from io import BytesIO
from pathlib import Path
from PyQt6 import QtWidgets
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader

from utils.paths import resource_path


def generate_season_accuracy_report(store_data: dict, emp_data: list[dict], team_data: list[dict]) -> None:
    """Generate and display accuracy reports for employees and teams for the full season.

    Args:
        store_data: Dictionary containing store data
        emp_data: List of employee data dictionaries
        team_data: List of team data dictionaries

    Raises:
        ValueError: If input parameters are invalid or required data is missing
        RuntimeError: If template files are missing or PDF generation fails
    """
    try:
        if not store_data:
            raise ValueError("store_data cannot be empty or None")
        if not isinstance(emp_data, list) or not isinstance(team_data, list):
            raise ValueError("emp_data and team_data must be lists")

        templates_path = resource_path("templates")
        if not templates_path or not Path(templates_path).exists():
            raise RuntimeError("Templates directory not found or invalid")

        env = Environment(loader=FileSystemLoader(templates_path))
        for template in ["season_emp_report.html", "season_team_report.html"]:
            template_path = Path(resource_path(f"templates/{template}"))
            if not template_path.exists():
                raise RuntimeError(f"Required template file not found: {template}")

        emp_template = env.get_template("season_emp_report.html")
        team_template = env.get_template("season_team_report.html")

        sorted_emp_data = sorted(emp_data, key=lambda x: (-x["uph"], -x["total_quantity"]))
        sorted_team_data = sorted(team_data, key=lambda x: x["zone_id"])

        html_emp = emp_template.render(page_headers=store_data, emp_data=sorted_emp_data)
        html_team = team_template.render(page_headers=store_data, team_data=sorted_team_data)
        full_html = (html_emp + "<div style='page-break-before: always;'></div>" + html_team)

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
        QtWidgets.QMessageBox.warning(
            None,
            "Data Validation Error",
            f"Invalid or missing input data while preparing the season accuracy report.\n\nDetails:\n{str(e)}"
        )
        raise

    except RuntimeError as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Report Generation Error",
            f"Failed to generate the season accuracy report due to missing templates or PDF generation issues.\n\nDetails:\n{str(e)}"
        )
        raise

    except Exception as e:
        QtWidgets.QMessageBox.warning(
            None,
            "Unexpected Error",
            f"An unexpected failure occurred during season accuracy report generation.\nThis may indicate missing templates, corrupt input data, or an unhandled edge case.\n\nDetails:\n{str(e)}"
        )
        raise