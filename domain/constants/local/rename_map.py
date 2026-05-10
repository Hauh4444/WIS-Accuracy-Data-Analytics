LOCAL_CONTEXT_RENAME_MAP = {
    "JobDateTime": "job_datetime",
    "StoreName": "store_name",
    "Address": "store_address",
    "PrintDate": "print_date",
    "PrintTime": "print_time",
}

LOCAL_EMP_RENAME_MAP = {
    "EmpNo": "EmpID",
    "TotalEXTPRICE": "TotalPrice",
    "DiscrepancyDollars": "ZoneErrorTotal",
    "DiscrepancyTags": "ZoneErrorTags",
}

LOCAL_DISCREPANCY_RENAME_MAP = {
    "EmpNo": "EmpID",
    "TagNo": "Tag",
    "EXTPRICE": "Price",
    "OrigQty": "CountedQty",
    "DiscrepancyDollars": "LineError",
}

LOCAL_ZONE_RENAME_MAP = {
    "TotalEXTPRICE": "TotalPrice",
    "DiscrepancyDollars": "ZoneErrorTotal",
    "DiscrepancyTags": "ZoneErrorTags",
}

LOCAL_AGGREGATE_CONTEXT_RENAME_MAP = {
    "PrintDate": "print_date",
    "PrintTime": "print_time",
    "StartDate": "start_date",
    "EndDate": "end_date",
}

LOCAL_AGGREGATE_EMP_RENAME_MAP = {
    "EmpNo": "EmpID",
    "EmployeeName": "EmpName",
    "AverageTags": "TotalTags",
    "AverageQty": "TotalQty",
    "AveragePrice": "TotalPrice",
    "AverageZoneErrorTotal": "ZoneErrorTotal",
    "AverageZoneErrorTags": "ZoneErrorTags",
    "AverageHours": "Hours",
}

LOCAL_AGGREGATE_ZONE_RENAME_MAP = {
    "ZoneDescription": "ZoneDesc",
    "AverageTags": "TotalTags",
    "AverageQty": "TotalQty",
    "AveragePrice": "TotalPrice",
    "AverageZoneErrorTotal": "ZoneErrorTotal",
    "AverageZoneErrorTags": "ZoneErrorTags",
}

EMP_RENAME_MAP = {
    "EmpID": "emp_id",
    "EmpName": "emp_name",
    "TotalPrice": "total_price",
    "TotalTags": "total_tags",
    "TotalQty": "total_qty",
    "ZoneErrorTotal": "zone_error_total",
    "ZoneErrorTags": "zone_error_tags",
    "ZoneErrorPercent": "zone_error_percent",
    "ZoneErrors": "zone_errors",
    "Hours": "hours",
    "UPH": "uph",
}

ZONE_RENAME_MAP = {
    "ZoneID": "zone_id",
    "ZoneDesc": "zone_desc",
    "TotalTags": "total_tags",
    "TotalPrice": "total_price",
    "TotalQty": "total_qty",
    "ZoneErrorTotal": "zone_error_total",
    "ZoneErrorTags": "zone_error_tags",
    "ZoneErrorPercent": "zone_error_percent",
}

AGGREGATE_EMP_RENAME_MAP = {
    "EmpID": "emp_id",
    "EmpName": "emp_name",
    "TotalPrice": "total_price",
    "TotalTags": "total_tags",
    "TotalQty": "total_qty",
    "ZoneErrorTotal": "zone_error_total",
    "ZoneErrorTags": "zone_error_tags",
    "ZoneErrorPercent": "zone_error_percent",
    "ZoneErrors": "zone_errors",
    "Hours": "hours",
    "UPH": "uph",
    "TotalStores": "total_stores",
}

AGGREGATE_ZONE_RENAME_MAP = {
    "ZoneID": "zone_id",
    "ZoneDesc": "zone_desc",
    "TotalTags": "total_tags",
    "TotalPrice": "total_price",
    "TotalQty": "total_qty",
    "ZoneErrorTotal": "zone_error_total",
    "ZoneErrorTags": "zone_error_tags",
    "ZoneErrorPercent": "zone_error_percent",
    "TotalStores": "total_stores",
}