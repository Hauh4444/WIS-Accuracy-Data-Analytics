from domain.dto.report_context import StoreReportContext, AggregateReportContext


class LocalStoreService:

    def __init__(self, repo, mapper):
        self.repo = repo
        self.mapper = mapper

    def fetch_store_data(self, store_number) -> StoreReportContext:
        df = self.repo.get_store_info(store_number)

        return self.mapper.to_store_context(df)

    def fetch_aggregate_store_data(self, date_range) -> AggregateReportContext:
        return self.mapper.to_aggregate_context(date_range)