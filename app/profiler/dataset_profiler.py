"""Deterministic profiling for pandas datasets."""

import pandas as pd

from app.schemas.dataset import DatasetProfile


class DatasetProfiler:
    """Create a compact profile from a pandas DataFrame."""

    def profile(self, data: pd.DataFrame, target_column: str) -> DatasetProfile:
        """Return a profile for ``data`` using ``target_column`` as the target."""
        if target_column not in data.columns:
            raise ValueError(f"Target column '{target_column}' was not found")

        target = data[target_column]
        numerical_columns = [
            column
            for column in data.columns
            if pd.api.types.is_numeric_dtype(data[column].dtype)
        ]
        categorical_columns = [
            column
            for column in data.columns
            if (
                pd.api.types.is_object_dtype(data[column].dtype)
                or pd.api.types.is_string_dtype(data[column].dtype)
                or isinstance(data[column].dtype, pd.CategoricalDtype)
                or pd.api.types.is_bool_dtype(data[column].dtype)
            )
        ]
        missing_value_columns = {
            column: int(missing_count)
            for column, missing_count in data.isna().sum().items()
            if missing_count > 0
        }
        target_unique_values = int(target.nunique(dropna=True))
        target_is_categorical = (
            pd.api.types.is_object_dtype(target.dtype)
            or pd.api.types.is_string_dtype(target.dtype)
            or isinstance(target.dtype, pd.CategoricalDtype)
            or pd.api.types.is_bool_dtype(target.dtype)
        )
        task_type = (
            "classification"
            if target_is_categorical or target_unique_values <= 20
            else "regression"
        )
        target_distribution = {
            str(value): int(count)
            for value, count in target.value_counts(dropna=False).items()
        }

        return DatasetProfile(
            rows=int(len(data)),
            columns=int(len(data.columns)),
            target_column=target_column,
            task_type=task_type,
            numerical_columns=numerical_columns,
            categorical_columns=categorical_columns,
            missing_value_columns=missing_value_columns,
            duplicate_rows=int(data.duplicated().sum()),
            unique_target_values=target_unique_values,
            target_distribution=target_distribution,
        )