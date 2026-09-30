"""Pydantic schemas for ML experiment configuration and results."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class ExperimentConfig(BaseModel):
    """Configuration for an ML experiment before execution."""

    experiment_id: str = Field(min_length=1)
    task_type: Literal["classification", "regression"]
    target_column: str = Field(min_length=1)
    model: str = Field(min_length=1)
    preprocessing: list[str]
    hyperparameters: dict[str, Any]
    evaluation_metric: str = Field(min_length=1)


class ExperimentResult(BaseModel):
    """Outcome of an executed ML experiment."""

    experiment_id: str = Field(min_length=1)
    status: Literal["success", "failed"]
    metrics: dict[str, float]
    training_time_seconds: float = Field(ge=0)
    observations: list[str]
