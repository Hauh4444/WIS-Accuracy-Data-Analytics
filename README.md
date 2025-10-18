# WIS Accuracy Data Analytics

A professional **Windows-only** Python application for generating WIS International accuracy reports using inventory data. Features a Qt6-based graphical interface with two-step database loading, employee hours input, store data integration, and Jinja2 templating for professional PDF report generation.

## Features

- **Windows-Only Application**: Designed exclusively for Windows with Microsoft Access database connectivity
- **Two-Step Database Loading**: 
  - Primary: Job Number input for automatic database path resolution (`C:\WISDOM\JOBS\{job_number}\11355\{job_number}.MDB`)
  - Fallback: Manual file browser for custom database selection
- **Store Data Integration**: Automatic loading of store information (name, address, inventory datetime) from WISE database
- **Employee Hours Input**: Interactive interface for entering employee work hours with UPH calculations
- **Team Zone Analytics**: Comprehensive team and zone-based discrepancy analysis
- **Professional Reports**: Three integrated reports (Employee, Team, Discrepancy) rendered as PDF with store headers and opened in browser for printing
- **Qt6 GUI**: Clean, professional interface for data input and report generation
- **Comprehensive Testing**: 67+ test cases covering all functionality with mock database connections
- **Data Models**: Comprehensive database table models for WISE Info, UPH, Details, Zone, Tag, and TagRange tables

## Installation

**Windows Only**: This application requires Windows with Microsoft Access database drivers.

1. Clone the repository:
   ```bash 
   git clone https://github.com/Hauh4444/WIS-Accuracy-Data-Analytics.git
   cd WIS-Accuracy-Data-Analytics
   ```

2. Create and activate virtual environment:
   ```bash 
   python -m venv venv
   venv\Scripts\activate
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
3. **Store Data Loading**: Store information (name, address, inventory datetime) is automatically loaded from the WISE database
4. **Employee Hours Input**: Enter work hours for each employee in the interactive interface with UPH calculations
5. **Data Processing**: Employee, team, and store data is loaded, validated, and processed with discrepancy calculations
6. **Report Generation**: Click "Print" to generate three integrated accuracy reports (Employee, Team, and Discrepancy) with store headers
7. **PDF Output**: Combined report is generated as a single PDF with page breaks and opened in browser for printing

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

Run the comprehensive test suite (67+ test cases):

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test files
python -m pytest tests/test_load_store_data.py -v
python -m pytest tests/test_load_emp_data.py -v
python -m pytest tests/test_load_team_data.py -v
python -m pytest tests/test_report_generator.py -v

# Run with coverage (optional)
python -m pytest tests/ --cov=services --cov-report=html
```

### Test Coverage

The test suite includes comprehensive coverage for:
- **Store Data Loading**: Database connectivity, error handling, data validation
- **Employee Data Processing**: UPH calculations, discrepancy analysis, null value handling
- **Team Data Processing**: Zone-based analytics, zone number handling
- **Report Generation**: PDF creation with three integrated reports (Employee, Team, Discrepancy), template rendering, error scenarios
- **UI Components**: Window initialization, user interactions, data validation
- **Database Operations**: Connection management, query execution, error recovery

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
│   ├── load_emp_data.py           # Employee data loading with UPH calculations
│   ├── load_team_data.py          # Team zone data loading with discrepancy analysis
│   ├── load_store_data.py         # Store data loading from WISE database
│   ├── models.py                  # Database table models (WISE Info, UPH, Details, Zone, Tag, etc.)
│   ├── report_generator.py        # PDF report generation with store headers
│   └── resource_utils.py          # Resource path utilities
├── styles/                        # Qt stylesheets
│   ├── emp_hour_input_row.qss
│   └── scrollbar.qss
├── templates/                     # HTML report templates
│   ├── disc_report.html           # Discrepancy report template
│   ├── emp_report.html            # Employee report template
│   └── team_report.html           # Team report template
├── tests/                        # Comprehensive test suite (67+ tests)
│   ├── test_database.py
│   ├── test_emp_hours_input_window.py
│   ├── test_load_data_dynamic_dialog.py
│   ├── test_load_data_manual_dialog.py
│   ├── test_load_emp_data.py
│   ├── test_load_store_data.py
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

- **Windows Only**: Requires Microsoft Access Driver (*.mdb, *.accdb) - **NOT compatible with Linux/Mac**
- **Database Path**: `C:\WISDOM\JOBS\{job_number}\11355\{job_number}.MDB`
- **Supported Formats**: `.mdb` and `.accdb` files
- **Required Tables**: 
  - `tblWISEInfo` - Store information (name, address, inventory datetime)
  - `tblUPH` - Employee data (employee number, name, tag count)
  - `tblDetailsOrg` - Employee tag assignments
  - `tblZone` - Zone information
  - `tblZoneChangeQueue` - Discrepancy tracking
  - `tblZoneChangeInfo` - Discrepancy details
  - `tblTag` - Tag totals and pricing
  - `tblTagRange` - Tag range summaries

## Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints for function parameters and return values
- Maintain clean, professional code with minimal comments
- Remove unused imports and dead code

### Testing
- **67+ comprehensive test cases** covering all major components
- Mock external dependencies (database connections, file I/O, Qt widgets)
- Test both success and failure scenarios
- **Store data loading tests** with proper error handling
- **Employee/team data processing tests** with discrepancy calculations
- **Report generation tests** with template validation
- **UI component tests** with proper mocking
- Fixed duplicate/useless tests to provide meaningful coverage

## License

This project is proprietary software for WIS International accuracy reporting.