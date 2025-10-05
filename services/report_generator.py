import tempfile
import webbrowser
from io import BytesIO
from pathlib import Path
from PyQt6 import QtWidgets
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader

from services.resource_utils import resource_path


def generate_accuracy_report(store_data: dict, emp_data: list[dict], team_data: list[dict]) -> None:
    """Generate and display accuracy reports for employees and teams.
    
    Args:
        store_data: Dictionary containing store data
        emp_data: List of employee data dictionaries
        team_data: List of team data dictionaries
    """
    for var, expected_type, name in [(store_data, dict, "store_data"), (emp_data, list, "emp_data"), (team_data, list, "team_data")]:
        if not isinstance(var, expected_type):
            QtWidgets.QMessageBox.critical(None, "Input Error", f"{name} must be a {expected_type.__name__}")
            return

    try:
        templates_path = resource_path("templates")
        env = Environment(loader=FileSystemLoader(templates_path))

        for template in ["emp_report.html", "team_report.html", "disc_report.html"]:
            if not Path(resource_path(f"templates/{template}")).exists():
                QtWidgets.QMessageBox.critical(None, "Template Error", f"{template} template not found")
                return

        emp_template = env.get_template("emp_report.html")
        team_template = env.get_template("team_report.html")
        disc_template = env.get_template("disc_report.html")
        html_emp = emp_template.render(page_headers=store_data, emp_data=emp_data)
        html_team = team_template.render(page_headers=store_data, team_data=team_data)
        html_disc = disc_template.render(page_headers=store_data, emp_data=emp_data)
        full_html = (
            html_emp + "<div style='page-break-before: always;'></div>" +
            html_team + "<div style='page-break-before: always;'></div>" +
            html_disc
        )

        pdf_buffer = BytesIO()
        result = pisa.CreatePDF(full_html, pdf_buffer)
        if result.err:
            QtWidgets.QMessageBox.critical(None, "PDF Error", "An error occurred while generating the PDF")
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_buffer.getvalue())
            tmp_file.flush()
            pdf_path = Path(tmp_file.name).resolve()
            if not pdf_path.exists():
                QtWidgets.QMessageBox.critical(None, "File Error", "Failed to create temporary PDF file")
                return
            webbrowser.open(f"file://{pdf_path}")

    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Unexpected Error", f"Failed to generate report:\n{e}")
