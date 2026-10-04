import pandas as pd
import pytest

from app.reporting.report_generator import ReportGenerator
from app.schemas.dataset import DatasetProfile
from app.schemas.experiment import ExperimentConfig, ExperimentResult


@pytest.fixture
def dataset_profile() -> DatasetProfile:
    return DatasetProfile(
        rows=4,
        columns=2,
        target_column="target",
        task_type="classification",
        numerical_columns=["feature", "target"],
        categorical_columns=[],
        missing_value_columns={},
        duplicate_rows=0,
        unique_target_values=2,
        target_distribution={"0": 2, "1": 2},
    )


@pytest.fixture
def experiment_history() -> list[tuple[ExperimentConfig, ExperimentResult]]:
    first_config = ExperimentConfig(
        experiment_id="experiment-1",
        task_type="classification",
        target_column="target",
        model="logistic_regression",
        preprocessing=["standard_scaler"],
        hyperparameters={"C": 1.0},
        evaluation_metric="accuracy",
        planning_reason="Start with a baseline.",
    )
    first_result = ExperimentResult(
        experiment_id="experiment-1",
        status="success",
        metrics={"accuracy": 0.8},
        training_time_seconds=0.1,
        observations=["Baseline completed"],
    )
    second_config = ExperimentConfig(
        experiment_id="experiment-2",
        task_type="classification",
        target_column="target",
        model="random_forest",
        preprocessing=["standard_scaler"],
        hyperparameters={"n_estimators": 10},
        evaluation_metric="accuracy",
        planning_reason="Try a tree-based model for a different model family.",
    )
    second_result = ExperimentResult(
        experiment_id="experiment-2",
        status="success",
        metrics={"accuracy": 0.9},
        training_time_seconds=0.2,
        observations=["Improved validation accuracy"],
    )
    return [(first_config, first_result), (second_config, second_result)]


def create_report(
    dataset_profile: DatasetProfile,
    experiment_history: list[tuple[ExperimentConfig, ExperimentResult]],
):
    return ReportGenerator(
        objective="Classify records",
        dataset_profile=dataset_profile,
        experiment_history=experiment_history,
    ).generate()


def test_report_contains_objective(
    dataset_profile: DatasetProfile,
    experiment_history: list[tuple[ExperimentConfig, ExperimentResult]],
) -> None:
    report = create_report(dataset_profile, experiment_history)

    assert report["objective"] == "Classify records"


def test_report_contains_dataset_summary(
    dataset_profile: DatasetProfile,
    experiment_history: list[tuple[ExperimentConfig, ExperimentResult]],
) -> None:
    report = create_report(dataset_profile, experiment_history)

    assert report["dataset_summary"] == dataset_profile.model_dump()


def test_report_contains_all_experiments(
    dataset_profile: DatasetProfile,
    experiment_history: list[tuple[ExperimentConfig, ExperimentResult]],
) -> None:
    report = create_report(dataset_profile, experiment_history)

    assert [
        experiment["experiment_id"] for experiment in report["experiments"]
    ] == ["experiment-1", "experiment-2"]
    assert report["experiments"][0]["configuration"]["model"] == (
        "logistic_regression"
    )
    assert report["experiments"][0]["configuration"]["planning_reason"] == (
        "Start with a baseline."
    )


def test_report_selects_best_successful_experiment(
    dataset_profile: DatasetProfile,
    experiment_history: list[tuple[ExperimentConfig, ExperimentResult]],
) -> None:
    report = create_report(dataset_profile, experiment_history)

    assert report["best_experiment"]["experiment_id"] == "experiment-2"
    assert report["best_experiment"]["result"]["metrics"]["accuracy"] == 0.9


def test_failed_experiments_are_not_selected_as_best(
    dataset_profile: DatasetProfile,
    experiment_history: list[tuple[ExperimentConfig, ExperimentResult]],
) -> None:
    failed_config = experiment_history[0][0].model_copy(
        update={"experiment_id": "experiment-failed"}
    )
    failed_result = experiment_history[0][1].model_copy(
        update={
            "experiment_id": "experiment-failed",
            "status": "failed",
            "metrics": {"accuracy": 1.0},
        }
    )
    report = create_report(
        dataset_profile,
        experiment_history + [(failed_config, failed_result)],
    )

    assert report["best_experiment"]["experiment_id"] == "experiment-2"


def test_experiments_without_metric_are_not_selected(
    dataset_profile: DatasetProfile,
    experiment_history: list[tuple[ExperimentConfig, ExperimentResult]],
) -> None:
    missing_metric_config = experiment_history[0][0].model_copy(
        update={"experiment_id": "experiment-no-metric"}
    )
    missing_metric_result = experiment_history[0][1].model_copy(
        update={"experiment_id": "experiment-no-metric", "metrics": {}}
    )
    report = create_report(
        dataset_profile,
        [
            (missing_metric_config, missing_metric_result),
            *experiment_history,
        ],
    )

    assert report["best_experiment"]["experiment_id"] == "experiment-2"


def test_report_contains_observations(
    dataset_profile: DatasetProfile,
    experiment_history: list[tuple[ExperimentConfig, ExperimentResult]],
) -> None:
    report = create_report(dataset_profile, experiment_history)

    assert report["key_observations"] == [
        "Baseline completed",
        "Improved validation accuracy",
    ]


def test_report_contains_final_conclusion(
    dataset_profile: DatasetProfile,
    experiment_history: list[tuple[ExperimentConfig, ExperimentResult]],
) -> None:
    report = create_report(dataset_profile, experiment_history)

    assert "experiment-2" in report["final_conclusion"]
    assert "accuracy=0.9" in report["final_conclusion"]
