"""Pydantic schemas for agent decisions."""

from typing import Literal

from pydantic import BaseModel


class AgentDecision(BaseModel):
    """Experiment configuration selected by the planning model."""

    model: Literal["logistic_regression", "random_forest", "gradient_boosting"]
    preprocessing: list[Literal["standard_scaler"]]
    hyperparameters: dict
    evaluation_metric: Literal["accuracy"]
    reason: str