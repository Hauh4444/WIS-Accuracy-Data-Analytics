import tempfile
import webbrowser
from io import BytesIO
from pathlib import Path
from xhtml2pdf import pisa

from exceptions.report_exceptions import ReportExportError
from exceptions.file_exceptions import FileSaveError


class PdfExportService:

    @staticmethod
    def export(html: str):
        try:
            buffer = BytesIO()

            result = pisa.CreatePDF(html, buffer)
            if result.err:
                raise ReportExportError("PDF generation failed (xhtml2pdf error)")

            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(buffer.getvalue())
                    tmp.flush()
                    path = Path(tmp.name).resolve()

            except Exception as e:
                raise FileSaveError("Failed to write PDF to disk") from e

            if not path.exists():
                raise FileSaveError("PDF file was not created")

            webbrowser.open(f"file://{path}")

        except (ReportExportError, FileSaveError):
            raise

        except Exception as e:
            raise ReportExportError("Unexpected error during PDF export") from e