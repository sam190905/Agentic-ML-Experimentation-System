import pandas as pd
import pytest

from app.evaluation.datasets import get_evaluation_datasets
from app.evaluation.baseline import BaselineStrategy
from app.evaluation.schemas import StrategyResult
from app.evaluation.evaluator import Evaluator
from app.schemas.experiment import ExperimentConfig, ExperimentResult


def test_datasets_load_correctly():
    datasets = get_evaluation_datasets()
    assert "iris" in datasets
    assert "breast_cancer" in datasets
    assert "wine" in datasets
    
    for name, ds in datasets.items():
        assert isinstance(ds["data"], pd.DataFrame)
        assert ds["target_column"] in ds["data"].columns
        assert isinstance(ds["objective"], str)


def test_baseline_strategy():
    datasets = get_evaluation_datasets()
    ds = datasets["iris"]
    
    baseline = BaselineStrategy()
    history = baseline.run(ds["data"], ds["target_column"], max_experiments=2)
    
    assert len(history) == 2
    assert history[0][0].model == "logistic_regression"
    assert history[1][0].model == "random_forest"
    
    assert history[0][1].status == "success"
    assert "accuracy" in history[0][1].metrics


def test_improvement_calculation():
    evaluator = Evaluator()
    config1 = ExperimentConfig(
        experiment_id="1", task_type="classification", target_column="t",
        model="logistic_regression", preprocessing=["standard_scaler"],
        hyperparameters={}, evaluation_metric="accuracy", planning_reason=""
    )
    res1 = ExperimentResult(
        experiment_id="1", status="success", metrics={"accuracy": 0.8},
        training_time_seconds=1.0, observations=[]
    )
    
    config2 = ExperimentConfig(
        experiment_id="2", task_type="classification", target_column="t",
        model="random_forest", preprocessing=["standard_scaler"],
        hyperparameters={}, evaluation_metric="accuracy", planning_reason=""
    )
    res2 = ExperimentResult(
        experiment_id="2", status="success", metrics={"accuracy": 0.95},
        training_time_seconds=1.0, observations=[]
    )
    
    history = [(config1, res1), (config2, res2)]
    
    result = evaluator._calculate_metrics("dummy", "baseline", history)
    
    assert result.first_experiment_score == 0.8
    assert result.best_score == 0.95
    assert result.best_model == "random_forest"
    assert pytest.approx(result.improvement_from_first) == 0.15
    assert result.total_training_time_seconds == 2.0
    
    assert len(result.steps) == 2
    assert result.steps[0].best_so_far == 0.8
    assert result.steps[1].best_so_far == 0.95
    assert result.best_scores_progression[1] == 0.8
    assert result.best_scores_progression[2] == 0.95


def test_evaluator_handles_provider_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "fallback")
    
    datasets = get_evaluation_datasets()
    ds = datasets["iris"]
    
    evaluator = Evaluator(provider="fallback")
    result = evaluator.evaluate_strategy("agent", "iris", ds["data"], ds["target_column"], ds["objective"], 2)
    
    assert result.strategy == "agent"
    assert result.provider == "fallback"
    assert result.experiments_run == 2
