import pytest
from pydantic import ValidationError

from app.schemas.experiment import ExperimentConfig, ExperimentResult


def test_valid_classification_experiment_config_can_be_created() -> None:
    config = ExperimentConfig(
        experiment_id="experiment-1",
        task_type="classification",
        target_column="target",
        model="logistic_regression",
        preprocessing=["standard_scaler"],
        hyperparameters={"C": 1.0},
        evaluation_metric="accuracy",
    )

    assert config.task_type == "classification"


def test_invalid_task_type_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ExperimentConfig(
            experiment_id="experiment-1",
            task_type="clustering",
            target_column="target",
            model="model",
            preprocessing=[],
            hyperparameters={},
            evaluation_metric="accuracy",
        )


def test_valid_experiment_result_can_be_created() -> None:
    result = ExperimentResult(
        experiment_id="experiment-1",
        status="success",
        metrics={"accuracy": 0.95},
        training_time_seconds=1.2,
        observations=["Baseline completed"],
    )

    assert result.status == "success"


def test_invalid_status_is_rejected() -> None:
    with pytest.raises(ValidationError):
        ExperimentResult(
            experiment_id="experiment-1",
            status="cancelled",
            metrics={},
            training_time_seconds=1.2,
            observations=[],
        )


def test_metrics_accept_numeric_values() -> None:
    result = ExperimentResult(
        experiment_id="experiment-1",
        status="success",
        metrics={"accuracy": 0.95, "correct_predictions": 95},
        training_time_seconds=1.2,
        observations=[],
    )

    assert result.metrics == {"accuracy": 0.95, "correct_predictions": 95.0}
