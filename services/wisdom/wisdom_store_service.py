from domain.dto.report_context import StoreReportContext


class WisdomStoreService:

    def __init__(self, repo, mapper):
        self.repo = repo
        self.mapper = mapper

    def fetch_store_data(self) -> StoreReportContext:
        df = self.repo.get_wise_info()

        return self.mapper.to_store_context(df)