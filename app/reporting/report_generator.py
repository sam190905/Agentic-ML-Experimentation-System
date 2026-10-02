"""Deterministic final reports for ML experiments."""

from typing import Any

from app.schemas.dataset import DatasetProfile
from app.schemas.experiment import ExperimentConfig, ExperimentResult


class ReportGenerator:
    """Build a structured report from stored experiment data."""

    def __init__(
        self,
        objective: str,
        dataset_profile: DatasetProfile,
        experiment_history: list[tuple[ExperimentConfig, ExperimentResult]],
    ) -> None:
        self.objective = objective
        self.dataset_profile = dataset_profile
        self.experiment_history = experiment_history

    def generate(self) -> dict[str, Any]:
        """Return a deterministic report using only persisted experiment values."""
        experiments = [
            {
                "experiment_id": config.experiment_id,
                "configuration": config.model_dump(),
                "result": result.model_dump(),
            }
            for config, result in self.experiment_history
        ]
        best_experiment = self._find_best_experiment()
        key_observations = [
            observation
            for _, result in self.experiment_history
            for observation in result.observations
        ]

        return {
            "objective": self.objective,
            "dataset_summary": self.dataset_profile.model_dump(),
            "experiments": experiments,
            "best_experiment": best_experiment,
            "key_observations": key_observations,
            "final_conclusion": self._build_conclusion(best_experiment),
        }

    def _find_best_experiment(self) -> dict[str, Any] | None:
        candidates = [
            (config, result)
            for config, result in self.experiment_history
            if result.status == "success"
            and config.evaluation_metric in result.metrics
        ]
        if not candidates:
            return None

        config, result = max(
            candidates,
            key=lambda item: item[1].metrics[item[0].evaluation_metric],
        )
        return {
            "experiment_id": config.experiment_id,
            "configuration": config.model_dump(),
            "result": result.model_dump(),
        }

    @staticmethod
    def _build_conclusion(best_experiment: dict[str, Any] | None) -> str:
        if best_experiment is None:
            return "No successful experiment with a recorded evaluation metric was available."

        configuration = best_experiment["configuration"]
        result = best_experiment["result"]
        metric = configuration["evaluation_metric"]
        value = result["metrics"][metric]
        return (
            f"Best experiment was '{best_experiment['experiment_id']}' "
            f"with {metric}={value}."
        )
