"""SQLite persistence for ML experiment configurations and results."""

import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path

from app.schemas.experiment import ExperimentConfig, ExperimentResult


class ExperimentMemory:
    """Persist experiment configurations and results in SQLite."""

    def __init__(self, database_path: str = "data/experiments.db") -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS experiments (
                        experiment_id TEXT PRIMARY KEY,
                        config_json TEXT NOT NULL,
                        result_json TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    )
                    """
                )

    def save_experiment(
        self, config: ExperimentConfig, result: ExperimentResult
    ) -> None:
        """Save one experiment, rejecting duplicate experiment IDs."""
        try:
            with closing(sqlite3.connect(self.database_path)) as connection:
                with connection:
                    connection.execute(
                        """
                        INSERT INTO experiments (
                            experiment_id, config_json, result_json, created_at
                        ) VALUES (?, ?, ?, ?)
                        """,
                        (
                            config.experiment_id,
                            config.model_dump_json(),
                            result.model_dump_json(),
                            datetime.now(timezone.utc).isoformat(),
                        ),
                    )
        except sqlite3.IntegrityError as error:
            raise ValueError(
                f"Experiment '{config.experiment_id}' already exists"
            ) from error

    def get_experiment(
        self, experiment_id: str
    ) -> tuple[ExperimentConfig, ExperimentResult] | None:
        """Return one stored experiment, if it exists."""
        with closing(sqlite3.connect(self.database_path)) as connection:
            row = connection.execute(
                """
                SELECT config_json, result_json
                FROM experiments
                WHERE experiment_id = ?
                """,
                (experiment_id,),
            ).fetchone()

        if row is None:
            return None
        return ExperimentConfig.model_validate_json(row[0]), ExperimentResult.model_validate_json(
            row[1]
        )

    def get_all_experiments(
        self,
    ) -> list[tuple[ExperimentConfig, ExperimentResult]]:
        """Return all stored experiments ordered by creation time."""
        with closing(sqlite3.connect(self.database_path)) as connection:
            rows = connection.execute(
                """
                SELECT config_json, result_json
                FROM experiments
                ORDER BY created_at ASC
                """
            ).fetchall()

        return [
            (
                ExperimentConfig.model_validate_json(config_json),
                ExperimentResult.model_validate_json(result_json),
            )
            for config_json, result_json in rows
        ]

    def get_best_experiment(
        self, metric: str, maximize: bool = True
    ) -> tuple[ExperimentConfig, ExperimentResult] | None:
        """Return the successful experiment with the best requested metric."""
        matching_experiments = [
            experiment
            for experiment in self.get_all_experiments()
            if experiment[1].status == "success" and metric in experiment[1].metrics
        ]
        if not matching_experiments:
            return None

        return (
            max if maximize else min
        )(matching_experiments, key=lambda experiment: experiment[1].metrics[metric])
