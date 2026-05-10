import pandas as pd
from typing import List

from mappers.base_mapper import BaseMapper
from domain.dto.employee import Employee, AggregateEmployee
from domain.constants.local.required_columns import REQUIRED_LOCAL_EMP_COLUMNS, REQUIRED_LOCAL_DISCREPANCY_COLUMNS, REQUIRED_AGGREGATE_EMP_COLUMNS
from domain.constants.local.rename_map import LOCAL_EMP_RENAME_MAP, LOCAL_DISCREPANCY_RENAME_MAP, LOCAL_AGGREGATE_EMP_RENAME_MAP, EMP_RENAME_MAP, AGGREGATE_EMP_RENAME_MAP


class LocalEmployeeMapper(BaseMapper):

    def to_employee_models(self, df_emp: pd.DataFrame, df_zone_errors_raw: pd.DataFrame) -> List[Employee]:
        df_emp = self._prepare(df_emp, required_columns=REQUIRED_LOCAL_EMP_COLUMNS, rename_map=LOCAL_EMP_RENAME_MAP)
        df_zone_errors = self._prepare(df_zone_errors_raw, required_columns=REQUIRED_LOCAL_DISCREPANCY_COLUMNS, rename_map=LOCAL_DISCREPANCY_RENAME_MAP)
        df_emp = self._fill(df_emp, ["EmpID", "EmpName", "TotalPrice", "TotalTags", "TotalQty", "ZoneErrorTotal", "ZoneErrorTags", "Hours"], 0)

        df_zone_errors_grouped = df_zone_errors.groupby("EmpID").apply(lambda g: g.to_dict(orient="records")).to_dict()

        df_emp["ZoneErrorPercent"] = df_emp["ZoneErrorTotal"].div(df_emp["TotalPrice"].replace(0, pd.NA)).fillna(0) * 100
        df_emp["ZoneErrors"] = df_emp["EmpID"].map(lambda emp_id: df_zone_errors_grouped.get(emp_id, []))
        df_emp["UPH"] = df_emp["TotalQty"].div(df_emp["Hours"].replace(0, pd.NA)).fillna(0)

        df = df_emp.sort_values(["UPH", "TotalQty"], ascending=[False, False])

        return self._map_dataframe(df, Employee, EMP_RENAME_MAP)

    def to_aggregate_employee_models(self, df: pd.DataFrame) -> List[AggregateEmployee]:
        df = self._prepare(df, required_columns=REQUIRED_AGGREGATE_EMP_COLUMNS, rename_map=LOCAL_AGGREGATE_EMP_RENAME_MAP)
        df = self._fill(df, ["EmpID", "EmpName", "TotalPrice", "TotalTags", "TotalQty", "ZoneErrorTotal", "ZoneErrorTags", "Hours"], 0)

        df["ZoneErrorPercent"] = df["ZoneErrorTotal"].div(df["TotalPrice"].replace(0, pd.NA)).fillna(0) * 100
        df["ZoneErrors"] = [[] for _ in range(len(df))]
        df["TotalStores"] = df.get("TotalStores", 0).fillna(0)
        df["UPH"] = df["TotalQty"].div((df["Hours"] * df["TotalStores"]).replace(0, pd.NA)).fillna(0)

        df = df.sort_values(["UPH", "TotalQty"], ascending=[False, False])

        return self._map_dataframe(df, AggregateEmployee, AGGREGATE_EMP_RENAME_MAP)