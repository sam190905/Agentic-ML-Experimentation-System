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
            config_id="lr-default",
            reason="The initial experiment establishes a regularized linear baseline.",
        ),
        AgentDecision(
            config_id="rf-deep",
            reason="The baseline provides a reference point, so evaluate a higher-capacity ensemble.",
        ),
        AgentDecision(
            config_id="gb-slow",
            reason="Compare a boosting configuration after evaluating the tree ensemble.",
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
    
    # Verify the planner was called exactly 3 times
    assert planner.plan.call_count == 3
    
    # Verify that the planner received updated experiment history correctly
    calls = planner.plan.call_args_list
    assert len(calls[0].args[2]) == 0
    assert len(calls[1].args[2]) == 1
    assert calls[1].args[2][0][0].config_id == "lr-default"
    assert len(calls[2].args[2]) == 2
    assert calls[2].args[2][0][0].config_id == "lr-default"
    assert calls[2].args[2][1][0].config_id == "rf-deep"
    
    assert [
        experiment_config.config_id
        for experiment_config, _ in result["experiment_history"]
    ] == [
        "lr-default",
        "rf-deep",
        "gb-slow",
    ]
    assert [
        experiment_config.planning_reason
        for experiment_config, _ in result["experiment_history"]
    ] == [
        "The initial experiment establishes a regularized linear baseline.",
        "The baseline provides a reference point, so evaluate a higher-capacity ensemble.",
        "Compare a boosting configuration after evaluating the tree ensemble.",
    ]


def test_graph_rejects_invalid_config_id(monkeypatch, tmp_path) -> None:
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
            config_id="rf-magic",
            reason="This config does not exist.",
        ),
    ]
    monkeypatch.setattr(
        graph_module,
        "ExperimentPlanner",
        MagicMock(return_value=planner),
    )

    initial_state = {
        "data": data,
        "run_id": "test-run-invalid",
        "objective": "Classify iris species",
        "target_column": "target",
        "dataset_profile": None,
        "current_experiment": None,
        "latest_result": None,
        "experiment_history": [],
        "experiment_count": 0,
        "max_experiments": 3,
    }

    import pytest
    with pytest.raises(ValueError, match="Invalid config_id"):
        graph_module.graph.invoke(initial_state)
