# WIS Accuracy Data Analytics

A professional **Windows-only** Python application for generating WIS International accuracy reports using inventory data. Features a Qt6-based graphical interface with two-step database loading, employee hours input, store data integration, and Jinja2 templating for professional PDF report generation.

## Features

- **Windows-Only Application**: Designed exclusively for Windows with Microsoft Access database connectivity
- **Two-Step Database Loading**: 
  - Primary: Job Number input for automatic database path resolution (`C:\WISDOM\JOBS\{job_number}\11355\{job_number}.MDB`)
  - Fallback: Manual file browser for custom database selection
- **Historical Inventory Stats**: Ability to load and view statistics from previous inventories for the same store 
- **Date Range Analytics**: Aggregated statistics calculated from all inventories completed during a user defined date range 
- **Conditional Availability**: Historical and Date Range stats are available only when local data has been saved for the relevant inventory or inventories
- **Store Data Integration**: Automatic loading of store information (name, address, inventory datetime) from WISE database
- **Employee Hours Input**: Interactive interface for entering employee work hours with UPH calculations
- **Zone Analytics**: Comprehensive zone and zone-based discrepancy analysis
- **Professional Reports**: Three integrated reports (Employee, zone, Discrepancy) rendered as PDF with store headers and opened in browser for printing
- **Qt6 GUI**: Clean, professional interface for data input and report generation
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
    pyinstaller --onefile --noconsole --additional-hooks-dir=packaging/hooks --add-data "assets/images;assets/images" --add-data "assets/ui;assets/ui" --add-data "assets/styles;assets/styles" --add-data "assets/templates;assets/templates" --add-data "assets/resources;assets/resources" -n AccuracyReport main.py
    ```

## Usage

### Application Workflow

1. **Launch the application** (`python main.py`)
2. **Inventory Data Mode Selection**: Select how inventory statistics should be loaded
   - **New Inventory Stats**: Load and process data from a WISE source database for a new inventory 
   - **Previous Inventory Stats**: Load statistics from a previously processed and locally saved inventory 
   - **Date Range Stats**: Load aggregated statistics from all inventories completed during a user defined range 
   - *Previous Inventory and Date Range options are only enabled if corresponding local data exists.*
3. **New Inventory Stats Workflow**:
   - **Database Loading**:
      - **Primary Method - Job Number Input**: Enter a Job Number to automatically connect to `C:\WISDOM\JOBS\{job_number}\11355\{job_number}.MDB`
      - **Fallback Method - File Browser**: If Job Number fails, browse and select database file manually (supports `.mdb` and `.accdb` files)
   - **Employee Hours Input**: Enter work hours for each employee in the interactive interface with UPH calculations
   - **Data Processing**: Employee, zone, and store data is loaded, validated, and processed with discrepancy calculations
   - **Report Generation**: Click "Print" to generate three integrated accuracy reports (Employee, zone, and Discrepancy) with store headers
4. **Previous Inventory Stats Workflow**:
   - **Database Loading**: Enter a Store Number to automatically resolve and load the locally saved inventory data for that store.
   - **Data Processing**: Employee, zone, and store data is loaded, validated, and processed with saved discrepancy data
   - **Report Generation**: Accuracy reports (Employee, Zone, and Discrepancy) are generated using the loaded historical inventory data.
5. **Date Range Stats Workflow**:
   - **Database Loading**: Automatically resolves and loads the locally saved data.
   - **Data Processing**: Employee, zone, and store data are loaded with aggregate data
   - **Report Generation**: Accuracy reports (Employee, Zone, and Discrepancy) are generated using the loaded aggregate data.
6. **PDF Output**: Combined report is generated as a single PDF with page breaks and opened in browser for printing

## Testing

### Test Suite

The application includes a comprehensive test suite:
1. Run all tests (requires PyQt6 + Windows environment)
    ```bash
    python -m pytest tests/ -v
    ```

2. Run with coverage reporting
    ```bash
    python -m pytest tests/ --cov=. --cov-report=html:htmlcov
    ```

## Dependencies

- **Python 3.12+**
- **PyQt6** - GUI framework
- **pyodbc** - Microsoft Access database connectivity
- **Jinja2** - HTML templating engine
- **xhtml2pdf** - HTML-to-PDF rendering
- **reportlab** - PDF generation support
- **PyInstaller** - Executable packaging (optional)

## Database Requirements

- **Windows Only**: Requires Microsoft Access Driver (*.mdb, *.accdb) - **NOT compatible with Linux/Mac**
- **Database Path**: `C:\WISDOM\JOBS\{job_number}\11355\{job_number}.MDB`
- **Supported Formats**: `.mdb` and `.accdb` files
- **Required Source Tables**: 
  - `tblWISEInfo` - WISE data, stores general inventory data
  - `tblTerminalControl` - Terminal data, stores employees active within the store
  - `tblEmpNames` - Employee data, maps employee numbers to names
  - `tblDetails` - Counting data, maps employees to tags
  - `tblDLoadErrors` - Download errors, stores duplicate tags
  - `tblZone` - Zone data, maps zones to descriptions
  - `tblZoneChangeQueue` - Discrepancy data, stores original quantities & assigned reason
  - `tblZoneChangeInfo` - Discrepancy data, stores corrected quantities
  - `tblTag` - Tag data, maps tags to total quantities & price
  - `tblTagRange` - Tag range data, maps tag ranges to zones & totals
- **Required Local Tables**: 
  - `tblInventory` - Inventory data, stores store information
  - `tblEmps` - Employee data, stores single inventory employee stats
  - `tblZones` - Zone data, stores single inventory zone stats

## Local Data Storage

- The application stores processed inventory and aggregate statistics in a Microsoft Access database located in the user’s local AppData directory:
    ```bash
    %LOCALAPPDATA%\WIS-Accuracy-Data-Analytics\accuracy.mdb
    ```
- All historical inventory stats are read from and written to this database. Previous Inventory and Date Range Stats workflows rely on this database and will only be available if the corresponding data has been previously saved.

## Project Structure

```
WIS-Accuracy-Data-Analytics
├── main.py
├── README.md
├── requirements.txt
├── .gitignore
├── assets/
│   ├── resources/
│   │   ├── accuracy.laccdb
│   │   └── accuracy.mdb
│   ├── styles/
│   │   ├── emp_hour_input_row.qss
│   │   ├── emp_select_row.qss
│   │   └── scrollbar.qss
│   ├── templates/
│   │   ├── aggregate_emp_report.html
│   │   ├── aggregate_zone_report.html
│   │   ├── disc_report.html
│   │   ├── emp_report.html
│   │   └── team_report.html
│   └── ui/
│       ├── emp_hours_window.ui
│       ├── emp_select_window.ui
│       ├── load_aggregate_data_dialog.ui
│       ├── load_local_data_dialog.ui
│       ├── load_source_data_dynamic_dialog.ui
│       ├── load_source_data_manual_dialog.ui
│       └── stats_source_dialog.ui
├── database/
│   └── __init__.py
│   ├── connection.py
├── models/
│   └── __init__.py
│   ├── local_models.py
│   ├── source_models.py
├── packaging/
│   └── hooks/
│       └── hook-xhtml2pdf.py
├── repositories/
│   └── __init__.py
│   ├── local_emp_repository.py
│   ├── local_store_repository.py
│   ├── local_zone_repository.py
│   ├── save_local_data_repository.py
│   ├── source_emp_repository.py
│   ├── source_store_repository.py
│   ├── source_zone_repository.py
├── services/
│   └── __init__.py
│   ├── load_local_emp_data.py
│   ├── load_local_store_data.py
│   ├── load_local_zone_data.py
│   ├── load_source_emp_data.py
│   ├── load_source_store_data.py
│   ├── load_source_zone_data.py
│   ├── save_local_data.py
├── tests/
├── utils/
│   └── __init__.py
│   ├── logging_config.py
│   ├── paths.py
│   ├── report_generator.py
│   ├── ui_utils.py
└── views/
    └── __init__.py
    ├── emp_hours_input_window.py
    ├── emp_select_window.py
    ├── load_aggregate_data_dialog.py
    ├── load_local_data_dialog.py
    ├── load_source_data_dynamic_dialog.py
    ├── load_source_data_manual_dialog.py
    ├── stats_source_dialog.py
```