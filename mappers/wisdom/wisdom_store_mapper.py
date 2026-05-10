import pandas as pd
from datetime import datetime

from mappers.base_mapper import BaseMapper
from domain.dto.report_context import StoreReportContext
from domain.constants.wisdom.required_columns import REQUIRED_WISDOM_STORE_COLUMNS
from domain.constants.wisdom.rename_map import WISDOM_CONTEXT_RENAME_MAP


class WisdomStoreMapper(BaseMapper):

    def to_store_context(self, df: pd.DataFrame) -> StoreReportContext | None:
        if df is None or df.empty:
            return None

        self._validate(df, required_columns=REQUIRED_WISDOM_STORE_COLUMNS)

        now = datetime.now()

        df["JobDateTime"] = df["JobDateTime"].fillna("")
        df["Name"] = df["Name"].fillna("")
        df["Address"] = df["Address"].fillna("")
        df["PrintDate"] = f"{now.month}/{now.day}/{now.year}"
        df["PrintTime"] = now.strftime("%I:%M:%S%p")

        return self._map_dataframe(df.head(1), StoreReportContext, WISDOM_CONTEXT_RENAME_MAP)[0]