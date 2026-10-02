"""Pydantic schemas for dataset profiling results."""

from typing import Literal

from pydantic import BaseModel


class DatasetProfile(BaseModel):
    """Summary statistics and column metadata for a dataset."""

    rows: int
    columns: int
    target_column: str
    task_type: Literal["classification", "regression"]
    numerical_columns: list[str]
    categorical_columns: list[str]
    missing_value_columns: dict[str, int]
    duplicate_rows: int
    unique_target_values: int
    target_distribution: dict[str, int]