"""Scripted evaluation-only deterministic strategy."""

import pandas as pd

from app.experimentation.catalog import get_catalog_entry
from app.experimentation.executor import ExperimentExecutor
from app.schemas.experiment import ExperimentConfig, ExperimentResult


class ScriptedStrategy:
    """
    A predetermined, deterministic alternative selection policy.
    Used exclusively to prove that the evaluation framework can
    detect differences in experiment strategy.
    
    Sequence: rf-deep -> gb-slow -> lr-strong-reg
    """
    
    def __init__(self) -> None:
        self.executor = ExperimentExecutor()
        self.sequence = [
            "rf-deep",
            "gb-slow",
            "lr-strong-reg"
        ]

    def run(
        self, data: pd.DataFrame, target_column: str, max_experiments: int = 3
    ) -> list[tuple[ExperimentConfig, ExperimentResult]]:
        
        history: list[tuple[ExperimentConfig, ExperimentResult]] = []
        
        for i in range(min(max_experiments, len(self.sequence))):
            config_id = self.sequence[i]
            entry = get_catalog_entry(config_id)
            
            config = ExperimentConfig(
                experiment_id=f"scripted-{config_id}",
                config_id=config_id,
                task_type="classification",  # assuming classification for simplicity
                target_column=target_column,
                model=entry.model,
                preprocessing=entry.preprocessing,
                hyperparameters=entry.hyperparameters,
                evaluation_metric=entry.evaluation_metric,
                planning_reason=f"Scripted fixed order: {i + 1}"
            )
            
            result = self.executor.execute(data, config)
            history.append((config, result))
            
        return history
