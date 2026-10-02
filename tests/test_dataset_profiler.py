import pandas as pd
import pytest

from app.profiler.dataset_profiler import DatasetProfiler


def test_basic_profile_creation() -> None:
    data = pd.DataFrame({"feature": [1, 2, 3], "target": ["a", "b", "a"]})

    profile = DatasetProfiler().profile(data, "target")

    assert profile.rows == 3
    assert profile.columns == 2
    assert profile.target_column == "target"
    assert profile.unique_target_values == 2
    assert profile.target_distribution == {"a": 2, "b": 1}


def test_target_column_validation() -> None:
    data = pd.DataFrame({"feature": [1, 2, 3]})

    with pytest.raises(ValueError, match="Target column 'target' was not found"):
        DatasetProfiler().profile(data, "target")


def test_numerical_and_categorical_column_detection() -> None:
    data = pd.DataFrame(
        {
            "numeric": [1, 2, 3],
            "category": ["a", "b", "a"],
            "target": [0, 1, 0],
        }
    )

    profile = DatasetProfiler().profile(data, "target")

    assert profile.numerical_columns == ["numeric", "target"]
    assert profile.categorical_columns == ["category"]


def test_missing_value_counting() -> None:
    data = pd.DataFrame(
        {
            "complete": [1, 2, 3],
            "incomplete": [1, None, None],
            "target": ["a", "b", "a"],
        }
    )

    profile = DatasetProfiler().profile(data, "target")

    assert profile.missing_value_columns == {"incomplete": 2}


def test_duplicate_row_counting() -> None:
    data = pd.DataFrame(
        {
            "feature": [1, 1, 2, 3],
            "target": ["a", "a", "b", "c"],
        }
    )

    profile = DatasetProfiler().profile(data, "target")

    assert profile.duplicate_rows == 1


def test_classification_detection() -> None:
    data = pd.DataFrame({"feature": [1, 2, 3], "target": ["yes", "no", "yes"]})

    profile = DatasetProfiler().profile(data, "target")

    assert profile.task_type == "classification"


def test_regression_detection() -> None:
    data = pd.DataFrame({"target": range(21)})

    profile = DatasetProfiler().profile(data, "target")

    assert profile.task_type == "regression"
