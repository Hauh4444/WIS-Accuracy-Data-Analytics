from dataclasses import dataclass


@dataclass
class BaseReportContext:
    print_date: str
    print_time: str


@dataclass
class StoreReportContext(BaseReportContext):
    store_name: str
    store_address: str
    job_datetime: str


@dataclass
class AggregateReportContext(BaseReportContext):
    start_date: str
    end_date: str