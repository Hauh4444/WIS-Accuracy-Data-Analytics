REQUIRED_WISDOM_STORE_COLUMNS = {
    "Name",
    "Address",
    "JobDateTime"
}

REQUIRED_WISDOM_EMP_COLUMNS = {
    "df_term": {"TerminalUser"},
    "df_emp": {"EmpNo", "Name"},
    "df_details": {"empno", "price", "qty", "tag"},
    "df_zone_errors_raw": {"Tag", "UPC", "LineError", "ZoneID"},
}

REQUIRED_WISDOM_ZONE_COLUMNS = {
    "df_zone": {"ZoneID", "ZoneDesc"},
    "df_totals": {"ZoneID", "TotalTags", "TotalPrice", "TotalQuantity"},
    "df_zone_errors_raw": {"Tag", "ZoneID", "UPC", "Price", "Quantity", "CountedQty", "LineError"},
    "df_manual_adjustments_raw": {"Tag", "ZoneID", "UPC", "Price", "Quantity", "CountedQty", "LineError"},
}