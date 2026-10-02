"""Execution of the currently supported ML experiment."""

import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from app.schemas.experiment import ExperimentConfig, ExperimentResult


class ExperimentExecutor:
    """Execute supported experiments with leakage-safe cross-validation."""

    def execute(
        self, data: pd.DataFrame, config: ExperimentConfig
    ) -> ExperimentResult:
        """Execute an experiment and return its result instead of raising errors."""

        try:
            self._validate_config(config)
            if config.target_column not in data.columns:
                raise ValueError(
                    f"Target column '{config.target_column}' was not found"
                )

            features = data.drop(columns=[config.target_column])
            target = data[config.target_column]
            pipeline = Pipeline(
                steps=[
                    ("preprocessing", StandardScaler()),
                    ("model", LogisticRegression(**config.hyperparameters)),
                ]
            )
            cross_validation = StratifiedKFold(
                n_splits=5, shuffle=True, random_state=42
            )
            scores = cross_validate(
                pipeline,
                features,
                target,
                cv=cross_validation,
                scoring="accuracy",
            )

            return ExperimentResult(
                experiment_id=config.experiment_id,
                status="success",
                metrics={"accuracy": float(scores["test_score"].mean())},
                training_time_seconds=float(scores["fit_time"].mean()),
                observations=["Completed 5-fold stratified cross-validation."],
            )
        except Exception as error:
            message = str(error).strip() or error.__class__.__name__
            return ExperimentResult(
                experiment_id=config.experiment_id,
                status="failed",
                metrics={},
                training_time_seconds=0.0,
                observations=[f"Experiment failed: {message}"],
            )

    @staticmethod
    def _validate_config(config: ExperimentConfig) -> None:
        if config.task_type != "classification":
            raise ValueError("Only classification experiments are supported")
        if config.model != "logistic_regression":
            raise ValueError("Only the logistic_regression model is supported")
        if config.preprocessing != ["standard_scaler"]:
            raise ValueError("Only standard_scaler preprocessing is supported")
        if config.evaluation_metric != "accuracy":
            raise ValueError("Only accuracy evaluation is supported")