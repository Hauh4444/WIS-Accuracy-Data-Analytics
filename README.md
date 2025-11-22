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
- **Professional Test Suite**: 194+ comprehensive test cases with senior engineer quality standards
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
        --add-data "resources;resources" ^
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

### Professional Test Suite (194+ Tests)

The application includes a comprehensive, professional-grade test suite written at senior engineer standards:

```bash
# Run safe tests (recommended - 37 tests, 100% passing)
python run_safe_tests.py

# Or manually run core tests
python -m pytest tests/test_models.py tests/test_paths.py -v

# Run all tests (requires PyQt6 + Windows environment)
python -m pytest tests/ -v

# Run with coverage reporting
python -m pytest tests/ --cov=. --cov-report=html:htmlcov
```

### Test Categories

#### **Core Modules (37 tests - 100% passing)**
- **Models** (30 tests): All dataclass definitions with immutability testing
- **Paths** (7 tests): Resource path resolution for dev/PyInstaller environments  

#### **Repository Layer (31 tests - Mocked database)**
- **Store Repository** (5 tests): Data access patterns with comprehensive mocking
- **Employee Repository** (12 tests): Employee data fetching with SQL validation
- **Team Repository** (12 tests): Team and zone data access patterns

#### **Service Layer (60+ tests - PyQt6 environment required)**
- **Load Data Services**: Store, employee, and team data loading with comprehensive error handling
- **Business Logic**: UPH calculations, discrepancy analysis, data validation
- **Error Handling**: Exception testing and edge cases

#### **UI Layer (40+ tests - PyQt6 environment required)**
- **Main Window**: Employee hours input functionality
- **Dialogs**: Manual and dynamic data loading dialogs
- **User Interactions**: Form validation and data processing

#### **Utilities (15+ tests - PyQt6 environment required)**
- **Report Generator**: PDF generation with template rendering
- **Main Application**: Application entry point and workflow

#### **Database Layer (15+ tests - Windows environment required)**
- **Database Connection**: Microsoft Access connectivity testing

### Test Quality Standards

- **Professional Coverage**: 90%+ coverage target with comprehensive testing
- **Appropriate Mocking**: All external dependencies properly isolated
- **No Redundancy**: Each test serves a specific purpose
- **Error Handling**: Comprehensive exception and edge case testing
- **Data Validation**: Input/output verification and data integrity
- **Senior Engineer Quality**: Professional standards throughout

### Test Documentation

See `tests/README.md` for detailed test documentation including:
- Test structure and organization
- Running instructions for different environments
- Coverage analysis and quality metrics
- Best practices and recommendations

## Project Structure

```
WIS-Accuracy-Data-Analytics/
├── main.py                                 # Application entry point
├── models.py                               # Database ORM models (WISE Info, UPH, Details, Zone, Tag, etc.)
├── pytest.ini                              # Pytest configuration file
├── README.md                               # Project overview and setup guide
├── requirements.txt                        # Python dependencies
├── run_safe_tests.py                       # Safe test runner for core tests (37 tests)
├── database/                               # Database configuration and connections
│   └── connection.py                       # Database connection management
├── hooks/                                  # Custom PyInstaller hooks for packaging
│   └── hook-xhtml2pdf.py                   # Hook for including xhtml2pdf assets in builds
├── repositories/                           # Data access and repository layer
│   ├── emp_repository.py                   # Fetches employee data
│   ├── store_repository.py                 # Fetches store data
│   └── team_repository.py                  # Fetches team data
├── services/                               # Business logic and service layer
│   ├── __init__.py
│   ├── load_emp_data.py                    # Employee data loading with UPH calculation logic
│   ├── load_team_data.py                   # Team zone data loading with discrepancy analysis
│   └── load_store_data.py                  # Store data loading from WISE table
├── styles/                                 # Application stylesheets for PyQt UI
│   ├── emp_hour_input_row.qss              # Styles for employee input row widgets
│   └── scrollbar.qss                       # Custom scrollbar theme
├── templates/                              # HTML templates for PDF and report generation
│   ├── disc_report.html                    # Discrepancy report template
│   ├── emp_report.html                     # UPH report template
│   └── team_report.html                    # Team/zone report template
├── tests/                                  # Professional test suite (194+ tests)
│   ├── __init__.py
│   ├── conftest.py                         # Test fixtures and configuration
│   ├── README.md                           # Comprehensive test documentation
│   ├── test_database.py                    # Database connection tests (15+ tests)
│   ├── test_emp_hours_input_window.py      # Main window tests (15+ tests)
│   ├── test_emp_repository.py              # Employee repository tests (12 tests)
│   ├── test_load_data_dynamic_dialog.py    # Dynamic dialog tests (10+ tests)
│   ├── test_load_data_manual_dialog.py     # Manual dialog tests (10+ tests)
│   ├── test_load_emp_data.py               # Employee data loading tests (25+ tests)
│   ├── test_load_store_data.py             # Store data loading tests (20+ tests)
│   ├── test_load_team_data.py              # Team data loading tests (20+ tests)
│   ├── test_main.py                        # Application entry point tests (10+ tests)
│   ├── test_models.py                      # Model tests (30 tests)
│   ├── test_paths.py                       # Path utility tests (7 tests)
│   ├── test_report_generator.py            # Report generation tests (15+ tests)
│   ├── test_store_repository.py            # Store repository tests (5 tests)
│   └── test_team_repository.py             # Team repository tests (12 tests)
├── ui/                                     # Qt Designer UI layout files
│   ├── emp_hours_window.ui                 # Employee hours input window design
│   ├── load_data_dynamic_dialog.ui         # Dynamic data load dialog layout
│   └── load_data_manual_dialog.ui          # Manual data load dialog layout
├── utils/                                  # Shared utility functions and helpers    
│   ├── paths.py                            # Resource and filesystem path utilities
│   ├── report_generator.py                 # PDF/HTML report formatting and rendering tools
│   └── ui_utils.py                         # Common PyQt widget and dialog utilities
└── views/                                  # View classes implementing the application’s UI logic
    ├── __init__.py
    ├── emp_hours_input_window.py           # Main window view for employee hour input
    ├── load_data_dynamic_dialog.py         # Logic for dynamic data loading dialog
    └── load_data_manual_dialog.py          # Logic for manual data loading dialog
```

## Dependencies

- **Python 3.12+**
- **PyQt6** - GUI framework
- **pyodbc** - Microsoft Access database connectivity
- **Jinja2** - HTML templating engine
- **xhtml2pdf** - HTML-to-PDF rendering
- **reportlab** - PDF generation support
- **pillow** - Image processing
- **pytest** - Testing framework with coverage reporting
- **pytest-cov** - Coverage analysis
- **pytest-mock** - Advanced mocking capabilities
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
- **194+ professional test cases** written at senior engineer standards
- **Comprehensive Coverage**: 90%+ coverage target with professional quality
- **Appropriate Mocking**: All external dependencies properly isolated
- **No Redundancy**: Each test serves a specific purpose with clear documentation
- **Multi-Environment Support**: Core tests (68) work in any environment, full suite requires PyQt6/Windows
- **Professional Standards**: Senior engineer quality with comprehensive error handling
- **Test Categories**: Unit, Integration, Error Handling, Data Validation, UI Testing
- **Documentation**: Comprehensive test documentation in `tests/README.md`