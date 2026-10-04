"""Pydantic schemas for the evaluation framework."""

from pydantic import BaseModel, Field

from app.schemas.experiment import ExperimentConfig, ExperimentResult


class ExperimentStepResult(BaseModel):
    experiment_index: int
    experiment_id: str
    config_id: str | None = None
    model: str | None = None
    score: float | None
    best_so_far: float | None
    training_time_seconds: float
    status: str
    failure_type: str | None = None


class StrategyResult(BaseModel):
    """Result of running a single strategy on a dataset."""
    dataset_name: str
    strategy: str
    provider: str
    experiments_run: int
    first_experiment_score: float | None
    best_score: float | None
    best_model: str | None
    improvement_from_first: float | None
    total_training_time_seconds: float
    failed_experiments: int
    experiment_history: list[tuple[ExperimentConfig, ExperimentResult]]
    steps: list[ExperimentStepResult] = []
    best_scores_progression: dict[int, float | None] = {}


class AggregateEvaluationResult(BaseModel):
    """Overall results across all datasets and strategies."""
    evaluations: list[StrategyResult]


class AgentTraceStep(BaseModel):
    experiment_index: int
    config_id: str
    model: str
    score: float | None
    best_so_far: float | None
    planning_reason: str | None
    failure_type: str | None = None


class BenchmarkComparison(BaseModel):
    dataset_name: str
    baseline_result: StrategyResult
    agent_result: StrategyResult
    final_score_difference: float | None
    best_score_difference_at_step: dict[int, float | None]
    experiments_to_reach_baseline_best: int | None
    final_best_model_baseline: str | None
    final_best_model_agent: str | None
    interpretation: str
    agent_trace: list[AgentTraceStep]


class BenchmarkReport(BaseModel):
    comparisons: list[BenchmarkComparison]
