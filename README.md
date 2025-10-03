# WIS Accuracy Data Analytics

A professional Python application for generating WIS International accuracy reports using inventory data. Features a Qt6-based graphical interface with two-step database loading, employee hours input, and Jinja2 templating for professional PDF report generation.

## Features

- **Two-Step Database Loading**: 
  - Primary: Job Number input for automatic database path resolution (`C:\WISDOM\JOBS\{job_number}\11355\{job_number}.MDB`)
  - Fallback: Manual file browser for custom database selection
- **Employee Hours Input**: Interactive interface for entering employee work hours
- **Qt6 GUI**: Clean, professional interface for data input and report generation
- **Professional Reports**: HTML templates rendered as PDFs and opened in browser for printing
- **Data Models**: Comprehensive database table models for UPH, Details, Zone, Tag, and TagRange tables
- **Windows-Only**: Designed for Windows with Microsoft Access database connectivity

## Installation

1. Clone the repository:
   ```bash 
   git clone https://github.com/Hauh4444/WIS-Accuracy-Data-Analytics.git
   cd WIS-Accuracy-Data-Analytics
   ```

2. Create and activate virtual environment:
   ```bash 
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. Install dependencies:
   ```bash 
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python main.py
   ```
   
5. (Optional) To build a standalone executable:
    ```bash
    pyinstaller --onefile --noconsole ^
        --additional-hooks-dir=hooks ^
        --add-data "ui;ui" ^
        --add-data "styles;styles" ^
        --add-data "templates;templates" ^
        -n AccuracyReport ^
        main.py
    ```

## Usage

### Application Workflow

1. **Launch the application** (`python main.py`)
2. **Database Loading**:
   - **Primary Method - Job Number Input**: Enter a Job Number to automatically connect to `C:\WISDOM\JOBS\{job_number}\11355\{job_number}.MDB`
   - **Fallback Method - File Browser**: If Job Number fails, browse and select database file manually (supports `.mdb` and `.accdb` files)
3. **Employee Hours Input**: Enter work hours for each employee in the interactive interface
4. **Data Processing**: Employee and team data is loaded, validated, and processed
5. **Report Generation**: Click "Print" to generate professional accuracy reports
6. **PDF Output**: Reports are generated as PDF and opened in browser for printing

### Building Standalone Executable

```bash
pyinstaller --onefile --noconsole \
    --additional-hooks-dir=hooks \
    --add-data "ui;ui" \
    --add-data "styles;styles" \
    --add-data "templates;templates" \
    -n AccuracyReport \
    main.py
```

## Testing

Run the comprehensive test suite:

```bash
# From project root
PYTHONPATH=. pytest -v

# Run specific test file
pytest tests/test_load_data_dynamic_dialog.py -v
```

## Project Structure

```
WIS-Accuracy-Data-Analytics/
├── main.py                          # Application entry point
├── README.md                        # This file
├── requirements.txt                 # Python dependencies
├── hooks/                          # PyInstaller hooks
│   └── hook-xhtml2pdf.py
├── services/                       # Core business logic
│   ├── __init__.py
│   ├── database.py                 # Database connection management
│   ├── load_emp_data.py           # Employee data loading
│   ├── load_team_data.py          # Team data loading
│   ├── models.py                  # Database table models (UPH, Details, Zone, Tag, etc.)
│   ├── report_generator.py        # PDF report generation
│   └── resource_utils.py          # Resource path utilities
├── styles/                        # Qt stylesheets
│   ├── emp_hour_input_row.qss
│   └── scrollbar.qss
├── templates/                     # HTML report templates
│   ├── emp_report.html
│   └── team_report.html
├── tests/                        # Comprehensive test suite
│   ├── test_database.py
│   ├── test_emp_hours_input_window.py
│   ├── test_load_data_dynamic_dialog.py
│   ├── test_load_data_manual_dialog.py
│   ├── test_load_emp_data.py
│   ├── test_load_team_data.py
│   └── test_report_generator.py
├── ui/                          # Qt Designer UI files
│   ├── emp_hours_window.ui
│   ├── load_data_dynamic_dialog.ui
│   └── load_data_manual_dialog.ui
└── views/                       # UI view classes
    ├── __init__.py
    ├── emp_hours_input_window.py
    ├── load_data_dynamic_dialog.py
    └── load_data_manual_dialog.py
```

## Dependencies

- **Python 3.12+**
- **PyQt6** - GUI framework
- **pyodbc** - Microsoft Access database connectivity
- **Jinja2** - HTML templating engine
- **xhtml2pdf** - HTML-to-PDF rendering
- **reportlab** - PDF generation support
- **pillow** - Image processing
- **pytest** - Testing framework
- **PyInstaller** - Executable packaging (optional)

## Database Requirements

- **Windows Only**: Microsoft Access Driver (*.mdb, *.accdb)
- **Database Path**: `C:\WISDOM\JOBS\{job_number}\11355\{job_number}.MDB`
- **Supported Formats**: `.mdb` and `.accdb` files

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Maintain clean, professional code with minimal comments
- Remove unused imports and dead code

### Testing
- Comprehensive test coverage for all major components
- Mock external dependencies (database connections, file I/O)
- Test both success and failure scenarios

## License

This project is proprietary software for WIS International accuracy reporting.