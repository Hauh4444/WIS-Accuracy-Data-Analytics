import pandas as pd
from datetime import datetime
from typing import List

from mappers.base_mapper import BaseMapper
from domain.dto.report_context import StoreReportContext, AggregateReportContext
from domain.constants.local.required_columns import REQUIRED_LOCAL_CONTEXT_COLUMNS
from domain.constants.local.rename_map import LOCAL_CONTEXT_RENAME_MAP, LOCAL_AGGREGATE_CONTEXT_RENAME_MAP


class LocalReportContextMapper(BaseMapper):

    def to_store_context(self, df: pd.DataFrame) -> StoreReportContext:
        self._validate(df, required_columns=REQUIRED_LOCAL_CONTEXT_COLUMNS)

        now = datetime.now()

        df["JobDateTime"] = df["JobDateTime"].fillna("")
        df["StoreName"] = df["StoreName"].fillna("")
        df["Address"] = df["Address"].fillna("")
        df["PrintDate"] = f"{now.month}/{now.day}/{now.year}"
        df["PrintTime"] = now.strftime("%I:%M:%S%p")

        return self._map_dataframe(df.head(1), StoreReportContext, LOCAL_CONTEXT_RENAME_MAP)[0]

    def to_aggregate_context(self, date_range: List[datetime]) -> AggregateReportContext:
        df = pd.DataFrame()

        now = datetime.now()

        df["PrintDate"] = f"{now.month}/{now.day}/{now.year}"
        df["PrintTime"] = now.strftime("%I:%M:%S%p")
        df["StartDate"] = date_range[0].strftime("%m/%d/%Y")
        df["EndDate"] = date_range[1].strftime("%m/%d/%Y")

        return self._map_dataframe(df, AggregateReportContext, LOCAL_AGGREGATE_CONTEXT_RENAME_MAP)