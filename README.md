# WIS-Accuracy-Data-Analytics

This Python application generates WIS International accuracy reports using inventory data. It provides a Qt6-based graphical interface and uses Jinja2 templates to produce HTML reports that are rendered as PDFs in the browser for printing. The PDFs are handled in memory and are not saved to disk.

## Features

- Qt6 GUI: Easy-to-use interface for loading inventory data and generating reports.
- Jinja2 Templating: Customizable HTML templates for professional report layouts.
- PDF Rendering in Browser: Reports are generated as PDFs in memory and opened in the default browser for printing.
- Inventory Data Integration: Works with employee and team data to create accurate reports.
- Standalone Executable: Can be packaged into an .exe for Windows distribution.

## Installation

1. Clone the repository
    ```bash 
    git clone https://github.com/Hauh4444/WIS-Accuracy-Data-Analytics.git
    ```
2. Activate your virtual environment and install dependencies:
    ```bash 
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```
3. Run the application:
    ```bash
    python main.py
    ```
4. (Optional) To build a standalone executable:
    ```bash
    pyinstaller --onefile main.py
    ```

## Usage

1. Launch the app (`python main.py` or the packaged `.exe`). 
2. Load employee or team inventory data. 
3. Choose the type of report (employee or team). 
4. The report is generated in memory and opened in your default browser. 
5. Print the PDF directly from the browser.

## Testing

1. Navigate to the root directory
2. Run the tests:
   ```bash
   PYTHONPATH=. pytest -v
   ```

## Dependencies

- Python 3.10+ 
- PyQt6 – GUI framework 
- Jinja2 – HTML templating 
- xhtml2pdf – HTML-to-PDF rendering

## Project Structure

```
.
├── main.py
├── README.md
├── services/
│   ├── __init__.py
│   ├── database.py
│   ├── load_emp_data.py
│   ├── load_team_data.py
│   ├── models.py
│   └── report_generator.py
├── styles/
│   └── scrollbar.qss
├── templates/
│   ├── emp_report.html
│   └── team_report.html
├── tests/
├── ui/
│   ├── emp_hours_window.ui
│   └── load_data_dialog.ui
├── venv/
└── views/
    ├── __init__.py
    ├── emp_hours_input_dialog.py
    └── load_data_dialog.py
```