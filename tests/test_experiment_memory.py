import sqlite3
import json

import pytest

from app.memory.experiment_memory import ExperimentMemory
from app.schemas.experiment import ExperimentConfig, ExperimentResult


def build_config(experiment_id: str) -> ExperimentConfig:
    return ExperimentConfig(
        experiment_id=experiment_id,
        task_type="classification",
        target_column="target",
        model="logistic_regression",
        preprocessing=["standard_scaler"],
        hyperparameters={"max_iter": 1000},
        evaluation_metric="accuracy",
        planning_reason="Use a simple baseline before exploring alternatives.",
    )


def build_result(
    experiment_id: str,
    metrics: dict[str, float],
    status: str = "success",
) -> ExperimentResult:
    return ExperimentResult(
        experiment_id=experiment_id,
        status=status,
        metrics=metrics,
        training_time_seconds=0.5,
        observations=["Test experiment"],
    )


def test_save_and_get_experiment(tmp_path) -> None:
    memory = ExperimentMemory(tmp_path / "experiments.db")
    config = build_config("experiment-1")
    result = build_result("experiment-1", {"accuracy": 0.92})

    memory.save_experiment(config, result)
    stored = memory.get_experiment("experiment-1")

    assert stored == (config, result)


def test_get_missing_experiment_returns_none(tmp_path) -> None:
    memory = ExperimentMemory(tmp_path / "experiments.db")

    assert memory.get_experiment("missing") is None


def test_get_legacy_experiment_without_planning_reason(tmp_path) -> None:
    database_path = tmp_path / "experiments.db"
    memory = ExperimentMemory(database_path)
    legacy_config = {
        "experiment_id": "legacy",
        "task_type": "classification",
        "target_column": "target",
        "model": "logistic_regression",
        "preprocessing": ["standard_scaler"],
        "hyperparameters": {"C": 1.0},
        "evaluation_metric": "accuracy",
    }
    result = build_result("legacy", {"accuracy": 0.8})
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO experiments (
                experiment_id, config_json, result_json, created_at
            ) VALUES (?, ?, ?, ?)
            """,
            (
                "legacy",
                json.dumps(legacy_config),
                result.model_dump_json(),
                "2026-01-01T00:00:00+00:00",
            ),
        )

    stored = memory.get_experiment("legacy")

    assert stored is not None
    assert stored[0].planning_reason == ""


def test_duplicate_experiment_id_is_rejected(tmp_path) -> None:
    memory = ExperimentMemory(tmp_path / "experiments.db")
    config = build_config("experiment-1")
    result = build_result("experiment-1", {"accuracy": 0.92})
    memory.save_experiment(config, result)

    with pytest.raises(ValueError):
        memory.save_experiment(config, result)


def test_get_all_experiments_returns_creation_order(tmp_path) -> None:
    memory = ExperimentMemory(tmp_path / "experiments.db")
    experiments = [
        (build_config("experiment-1"), build_result("experiment-1", {"accuracy": 0.8})),
        (build_config("experiment-2"), build_result("experiment-2", {"accuracy": 0.9})),
        (build_config("experiment-3"), build_result("experiment-3", {"accuracy": 0.85})),
    ]

    for config, result in experiments:
        memory.save_experiment(config, result)

    stored = memory.get_all_experiments()

    assert [config.experiment_id for config, _ in stored] == [
        "experiment-1",
        "experiment-2",
        "experiment-3",
    ]


def test_get_best_experiment_maximize(tmp_path) -> None:
    memory = ExperimentMemory(tmp_path / "experiments.db")
    experiments = [
        (build_config("low"), build_result("low", {"accuracy": 0.8})),
        (build_config("high"), build_result("high", {"accuracy": 0.95})),
    ]

    for config, result in experiments:
        memory.save_experiment(config, result)

    best = memory.get_best_experiment("accuracy", maximize=True)

    assert best is not None
    assert best[0].experiment_id == "high"


def test_get_best_experiment_minimize(tmp_path) -> None:
    memory = ExperimentMemory(tmp_path / "experiments.db")
    experiments = [
        (build_config("high-rmse"), build_result("high-rmse", {"rmse": 1.4})),
        (build_config("low-rmse"), build_result("low-rmse", {"rmse": 0.6})),
    ]

    for config, result in experiments:
        memory.save_experiment(config, result)

    best = memory.get_best_experiment("rmse", maximize=False)

    assert best is not None
    assert best[0].experiment_id == "low-rmse"


def test_failed_experiments_are_ignored(tmp_path) -> None:
    memory = ExperimentMemory(tmp_path / "experiments.db")
    successful_config = build_config("successful")
    failed_config = build_config("failed")
    memory.save_experiment(
        successful_config, build_result("successful", {"accuracy": 0.8})
    )
    memory.save_experiment(
        failed_config, build_result("failed", {"accuracy": 1.0}, status="failed")
    )

    best = memory.get_best_experiment("accuracy")

    assert best is not None
    assert best[0].experiment_id == "successful"


def test_experiments_without_requested_metric_are_ignored(tmp_path) -> None:
    memory = ExperimentMemory(tmp_path / "experiments.db")
    memory.save_experiment(
        build_config("without-metric"), build_result("without-metric", {"accuracy": 0.9})
    )
    memory.save_experiment(
        build_config("with-metric"), build_result("with-metric", {"rmse": 0.4})
    )

    best = memory.get_best_experiment("rmse", maximize=False)

    assert best is not None
    assert best[0].experiment_id == "with-metric"
