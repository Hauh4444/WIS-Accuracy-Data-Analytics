REQUIRED_LOCAL_CONTEXT_COLUMNS = {
    "JobDateTime",
    "StoreName",
    "Address",
}

REQUIRED_LOCAL_EMP_COLUMNS = {
    "EmpNo",
    "EmpName",
    "TotalTags",
    "TotalQty",
    "TotalEXTPRICE",
    "DiscrepancyDollars",
    "DiscrepancyTags",
    "Hours",
}

REQUIRED_LOCAL_DISCREPANCY_COLUMNS = {
    "EmpNo",
    "ZoneID",
    "TagNo",
    "UPC",
    "EXTPRICE",
    "OrigQty",
    "NewQty",
    "DiscrepancyDollars",
}

REQUIRED_LOCAL_ZONE_COLUMNS = {
    "ZoneID",
    "ZoneDesc",
    "TotalTags",
    "TotalQty",
    "TotalEXTPRICE",
    "DiscrepancyDollars",
    "DiscrepancyTags",
}

REQUIRED_AGGREGATE_EMP_COLUMNS = {
    "EmpNo",
    "EmployeeName",
    "AverageTags",
    "AverageQty",
    "AveragePrice",
    "AverageZoneErrorTotal",
    "AverageZoneErrorTags",
    "AverageHours",
    "TotalStores"
}

REQUIRED_AGGREGATE_ZONE_COLUMNS = {
    "ZoneID",
    "ZoneDescription",
    "AverageTags",
    "AverageQty",
    "AveragePrice",
    "AverageZoneErrorTotal",
    "AverageZoneErrorTags",
    "TotalStores",
}