# WIS Accuracy Data Analytics

A professional Python application for generating WIS International accuracy reports using inventory data. Features a Qt6-based graphical interface with two-step database loading and Jinja2 templating for professional PDF report generation.

## Features

- **Two-Step Database Loading**: 
  - Primary: Job ID input for automatic database path resolution
  - Fallback: Manual file browser for custom database selection
- **Qt6 GUI**: Clean, professional interface for data input and report generation
- **Professional Reports**: HTML templates rendered as PDFs in browser for printing
- **Cross-Platform**: Works on Windows and Linux with appropriate database drivers
- **Standalone Executable**: Can be packaged for Windows distribution

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

### Database Loading Process

1. **Launch the application** (`python main.py`)
2. **Primary Method - Job ID Input**:
   - Enter a Job ID in the first dialog
   - Application attempts to connect to: `C:\WISDOM\JOBS\{job_id}\11355\{job_id}.MDB`
3. **Fallback Method - File Browser** (if Job ID fails):
   - Browse and select database file manually
   - Supports `.mdb` and `.accdb` files
4. **Data Processing**: Employee and team data is loaded and validated
5. **Report Generation**: Professional accuracy reports are generated
6. **PDF Output**: Reports open in browser for printing

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
│   ├── models.py                  # Data models
│   ├── report_generator.py        # Report generation
│   └── resource_utils.py          # Resource path utilities
├── styles/                        # Qt stylesheets
│   ├── emp_hour_input_row.qss
│   └── scrollbar.qss
├── templates/                     # HTML report templates
│   ├── emp_report.html
│   └── team_report.html
├── tests/                        # Test suite
│   ├── test_database.py
│   ├── test_load_data_dynamic_dialog.py
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

- **Python 3.10+**
- **PyQt6** - GUI framework
- **pyodbc** - Database connectivity
- **Jinja2** - HTML templating
- **xhtml2pdf** - HTML-to-PDF rendering
- **PyInstaller** - Executable packaging (optional)

## Database Requirements

- **Windows**: Microsoft Access Driver (*.mdb, *.accdb)
- **Linux**: MDBTools (`sudo apt-get install mdbtools`)

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