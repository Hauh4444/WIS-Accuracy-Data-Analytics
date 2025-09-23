import tempfile
import webbrowser
from io import BytesIO
from pathlib import Path
from PyQt6 import QtWidgets
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader


def generate_employee_report(emp_data: list[dict], team_data: list[dict]) -> None:
    if not isinstance(emp_data, list):
        QtWidgets.QMessageBox.critical(None, "Input Error", "emp_data must be a list of dictionaries.")
        return
    if not isinstance(team_data, list):
        QtWidgets.QMessageBox.critical(None, "Input Error", "team_data must be a list of dictionaries.")
        return

    try:
        env = Environment(loader=FileSystemLoader("templates"))

        if not Path("templates/emp_report.html").exists():
            QtWidgets.QMessageBox.critical(None, "Template Error", "emp_report.html template not found.")
            return
        if not Path("templates/team_report.html").exists():
            QtWidgets.QMessageBox.critical(None, "Template Error", "team_report.html template not found.")
            return

        sorted_emp_data = sorted(emp_data, key=lambda x: -x.get("uph", 0))
        html_employee = env.get_template("emp_report.html").render(results=sorted_emp_data)
        #sorted_team_data = sorted(team_data, key=lambda x: x.get("department_number", 0))
        html_team = env.get_template("team_report.html").render(results=team_data)

        full_html = html_employee + '<div style="page-break-before: always;"></div>' + html_team

        pdf_buffer = BytesIO()
        result = pisa.CreatePDF(full_html, pdf_buffer)
        if result.err:
            QtWidgets.QMessageBox.critical(None, "PDF Error", "An error occurred while generating the PDF.")
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_buffer.getvalue())
            tmp_file.flush()
            pdf_path = Path(tmp_file.name).resolve()
            if not pdf_path.exists():
                QtWidgets.QMessageBox.critical(None, "File Error", "Failed to create temporary PDF file.")
                return
            webbrowser.open(f"file://{pdf_path}")

    except Exception as e:
        QtWidgets.QMessageBox.critical(None, "Unexpected Error", f"Failed to generate report:\n{e}")
