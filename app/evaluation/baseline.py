"""Fixed baseline experimentation strategy."""

import pandas as pd

from app.experimentation.executor import ExperimentExecutor
from app.schemas.experiment import ExperimentConfig, ExperimentResult


class BaselineStrategy:
    """Runs a fixed set of ML experiments in order."""

    def __init__(self) -> None:
        self.executor = ExperimentExecutor()

    def run(self, data: pd.DataFrame, target_column: str, max_experiments: int = 3) -> list[tuple[ExperimentConfig, ExperimentResult]]:
        from app.experimentation.catalog import get_baseline_ordering
        
        ordering = get_baseline_ordering()
        configs = []
        for i, entry in enumerate(ordering):
            configs.append(
                ExperimentConfig(
                    experiment_id=f"baseline-{entry.config_id}",
                    config_id=entry.config_id,
                    task_type="classification",
                    target_column=target_column,
                    model=entry.model,
                    preprocessing=entry.preprocessing,
                    hyperparameters=entry.hyperparameters,
                    evaluation_metric=entry.evaluation_metric,
                    planning_reason=f"Baseline fixed order: {i + 1}",
                )
            )

        history = []
        for i in range(min(max_experiments, len(configs))):
            config = configs[i]
            result = self.executor.execute(data, config)
            history.append((config, result))
            
        return history
