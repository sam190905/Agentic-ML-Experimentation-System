import importlib
from unittest.mock import MagicMock

import pandas as pd
from sklearn.datasets import load_iris

from app.memory.experiment_memory import ExperimentMemory
from app.schemas.agent import AgentDecision


def test_graph_runs_until_max_experiments(monkeypatch, tmp_path) -> None:
    iris = load_iris()
    data = pd.DataFrame(
        iris.data,
        columns=[
            "sepal_length",
            "sepal_width",
            "petal_length",
            "petal_width",
        ],
    )
    data["target"] = iris.target

    graph_module = importlib.import_module("app.agent.graph")
    monkeypatch.setattr(
        graph_module,
        "ExperimentMemory",
        lambda: ExperimentMemory(str(tmp_path / "experiments.db")),
    )
    planner = MagicMock()
    planner.plan.side_effect = [
        AgentDecision(
            model="logistic_regression",
            preprocessing=["standard_scaler"],
            hyperparameters={"C": 1.0, "max_iter": 1000},
            evaluation_metric="accuracy",
            reason="Start with a baseline configuration.",
        ),
        AgentDecision(
            model="logistic_regression",
            preprocessing=["standard_scaler"],
            hyperparameters={"C": 0.1, "max_iter": 1000},
            evaluation_metric="accuracy",
            reason="Try stronger regularization.",
        ),
        AgentDecision(
            model="logistic_regression",
            preprocessing=["standard_scaler"],
            hyperparameters={"C": 10.0, "max_iter": 1000},
            evaluation_metric="accuracy",
            reason="Try weaker regularization.",
        ),
    ]
    monkeypatch.setattr(
        graph_module,
        "ExperimentPlanner",
        MagicMock(return_value=planner),
    )

    initial_state = {
        "data": data,
        "run_id": "test-run",
        "objective": "Classify iris species",
        "target_column": "target",
        "dataset_profile": None,
        "current_experiment": None,
        "latest_result": None,
        "experiment_history": [],
        "experiment_count": 0,
        "max_experiments": 3,
    }

    result = graph_module.graph.invoke(initial_state)

    assert result["dataset_profile"] is not None
    assert result["experiment_count"] == 3
    assert len(result["experiment_history"]) == 3
    assert all(
        experiment_result.status == "success"
        for _, experiment_result in result["experiment_history"]
    )
    assert [
        experiment_config.experiment_id
        for experiment_config, _ in result["experiment_history"]
    ] == [
        "test-run-experiment-1",
        "test-run-experiment-2",
        "test-run-experiment-3",
    ]
    assert planner.plan.call_count == 3
    assert [
        experiment_config.hyperparameters
        for experiment_config, _ in result["experiment_history"]
    ] == [
        {"C": 1.0, "max_iter": 1000},
        {"C": 0.1, "max_iter": 1000},
        {"C": 10.0, "max_iter": 1000},
    ]
    assert [
        experiment_config.planning_reason
        for experiment_config, _ in result["experiment_history"]
    ] == [
        "Start with a baseline configuration.",
        "Try stronger regularization.",
        "Try weaker regularization.",
    ]
