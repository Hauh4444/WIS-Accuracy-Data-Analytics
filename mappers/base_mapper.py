import pandas as pd
from typing import TypeVar, Type, List, Any

from exceptions.validation_exceptions import ValidationError

T = TypeVar("T")


class BaseMapper:

    @staticmethod
    def _validate(df: pd.DataFrame, *, required_columns: set | None = None, name: str = "DataFrame"):
        if df is None or df.empty:
            raise ValidationError(f"{name} is empty")

        if required_columns:
            missing = required_columns - set(df.columns)
            if missing:
                raise ValidationError(f"{name} missing columns: {sorted(missing)}")

    @staticmethod
    def _prepare(df: pd.DataFrame, *, required_columns: set | None = None, rename_map: dict | None = None, drop_empty: bool = True,) -> pd.DataFrame:
        BaseMapper._validate(df, required_columns=required_columns)

        df = df.copy()

        if rename_map:
            df = df.rename(columns=rename_map)

        if drop_empty and df.empty:
            return pd.DataFrame()

        return df

    @staticmethod
    def _fill(df: pd.DataFrame, columns: list[str], value: Any = 0) -> pd.DataFrame:
        for col in columns:
            if col in df.columns:
                df[col] = df[col].fillna(value)

        return df

    @staticmethod
    def _map_dataframe(df: pd.DataFrame, model: Type[T], field_map: dict) -> List[T] | T:
        if df is None or df.empty:
            return []

        results: List[T] = []

        for _, row in df.iterrows():
            kwargs = {
                model_field: row.get(df_column)
                for df_column, model_field in field_map.items()
            }
            results.append(model(**kwargs))

        return results