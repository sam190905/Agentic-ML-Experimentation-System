import pandas as pd
from sklearn.datasets import load_iris

from app.experimentation.executor import ExperimentExecutor
from app.schemas.experiment import ExperimentConfig


def build_iris_data() -> pd.DataFrame:
    iris = load_iris()
    return pd.DataFrame(
        iris.data,
        columns=[
            "sepal_length",
            "sepal_width",
            "petal_length",
            "petal_width",
        ],
    ).assign(target=iris.target)


def build_config(**overrides: object) -> ExperimentConfig:
    values: dict[str, object] = {
        "experiment_id": "iris-baseline",
        "task_type": "classification",
        "target_column": "target",
        "model": "logistic_regression",
        "preprocessing": ["standard_scaler"],
        "hyperparameters": {"max_iter": 1000},
        "evaluation_metric": "accuracy",
    }
    values.update(overrides)
    return ExperimentConfig(**values)


def test_successful_execution() -> None:
    result = ExperimentExecutor().execute(build_iris_data(), build_config())

    assert result.status == "success"


def test_accuracy_exists() -> None:
    result = ExperimentExecutor().execute(build_iris_data(), build_config())

    assert "accuracy" in result.metrics


def test_accuracy_range() -> None:
    result = ExperimentExecutor().execute(build_iris_data(), build_config())

    assert 0 <= result.metrics["accuracy"] <= 1


def test_training_time() -> None:
    result = ExperimentExecutor().execute(build_iris_data(), build_config())

    assert result.training_time_seconds >= 0


def test_experiment_id() -> None:
    result = ExperimentExecutor().execute(build_iris_data(), build_config())

    assert result.experiment_id == "iris-baseline"


def test_missing_target() -> None:
    config = build_config(target_column="missing_target")
    result = ExperimentExecutor().execute(build_iris_data(), config)

    assert result.status == "failed"


def test_unsupported_task() -> None:
    config = build_config(task_type="regression")
    result = ExperimentExecutor().execute(build_iris_data(), config)

    assert result.status == "failed"
