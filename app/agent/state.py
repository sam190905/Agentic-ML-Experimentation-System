"""State shared by the experimentation graph nodes."""

from typing import TypedDict

import pandas as pd

from app.schemas.dataset import DatasetProfile
from app.schemas.experiment import ExperimentConfig, ExperimentResult


class AgentState(TypedDict):
    """Data passed between the simple experimentation graph nodes."""

    data: pd.DataFrame
    run_id: str
    objective: str
    target_column: str
    dataset_profile: DatasetProfile | None
    current_experiment: ExperimentConfig | None
    latest_result: ExperimentResult | None
    experiment_history: list[tuple[ExperimentConfig, ExperimentResult]]
    experiment_count: int
    max_experiments: int