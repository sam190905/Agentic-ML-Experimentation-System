"""LLM-based experiment planning with structured output."""

import os
import time

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from app.schemas.agent import AgentDecision
from app.schemas.dataset import DatasetProfile
from app.schemas.experiment import ExperimentConfig, ExperimentResult


class ExperimentPlanner:
    """Select the next supported experiment configuration."""

    def __init__(self) -> None:
        load_dotenv()
        self.provider = os.getenv("LLM_PROVIDER", "gemini")
        if self.provider not in {"gemini", "fallback"}:
            raise ValueError(
                "LLM_PROVIDER must be either 'gemini' or 'fallback'"
            )
        self.model_name = os.getenv("LLM_MODEL", "gemini-3.8-flash")
        self.api_key = os.getenv("GEMINI_API_KEY")

    def plan(
        self,
        objective: str,
        dataset_profile: DatasetProfile,
        experiment_history: list[tuple[ExperimentConfig, ExperimentResult]],
    ) -> AgentDecision:
        """Ask the LLM to choose a supported experiment."""
        history = [
            {
                "experiment": config.model_dump(),
                "result": result.model_dump(),
            }
            for config, result in experiment_history
        ]
        if self.provider == "fallback":
            return self._fallback_decision(objective, experiment_history)

        prompt = f"""
You are selecting the next machine learning experiment for an experimentation system.

Analyze the dataset profile, consider the user objective, and inspect the previous
experiment results. Avoid repeating an identical configuration. Choose one supported
experiment and explain why it was selected.

Supported models:
- logistic_regression
- random_forest
- gradient_boosting

Supported preprocessing:
- standard_scaler

Supported evaluation metric:
- accuracy

Dataset profile:
{dataset_profile.model_dump_json()}

User objective:
{objective}

Previous experiments and results:
{history}

Return only a structured decision matching the AgentDecision schema.
"""
        structured_model = ChatGoogleGenerativeAI(
            model=self.model_name,
            google_api_key=self.api_key,
            temperature=0,
        ).with_structured_output(AgentDecision)
        for attempt in range(4):
            try:
                return structured_model.invoke(prompt)
            except Exception as error:
                if attempt == 3 or not self._is_transient_error(error):
                    raise
                time.sleep(2 ** (attempt + 1))

        raise RuntimeError("Planner invocation did not complete")

    @staticmethod
    def _fallback_decision(
        objective: str,
        experiment_history: list[tuple[ExperimentConfig, ExperimentResult]],
    ) -> AgentDecision:
        """Select an experiment with the deterministic development fallback."""
        tried_models = {config.model for config, _ in experiment_history}
        configurations = {
            "logistic_regression": {
                "C": 1.0,
                "max_iter": 200,
                "solver": "lbfgs",
            },
            "random_forest": {
                "n_estimators": 200,
                "random_state": 42,
                "n_jobs": -1,
            },
            "gradient_boosting": {
                "n_estimators": 100,
                "learning_rate": 0.1,
                "random_state": 42,
            },
        }
        for model in (
            "logistic_regression",
            "random_forest",
            "gradient_boosting",
        ):
            if model not in tried_models:
                return AgentDecision(
                    model=model,
                    preprocessing=["standard_scaler"],
                    hyperparameters=configurations[model],
                    evaluation_metric="accuracy",
                    reason=(
                        "Deterministic development/demo fallback selected "
                        f"{model} because it has not been tried yet for "
                        f"the objective: {objective}"
                    ),
                )

        return AgentDecision(
            model="logistic_regression",
            preprocessing=["standard_scaler"],
            hyperparameters={
                "C": 0.1,
                "max_iter": 200,
                "solver": "lbfgs",
            },
            evaluation_metric="accuracy",
            reason=(
                "Deterministic development/demo fallback selected "
                "logistic_regression with C=0.1 because all three supported "
                "models have already been tried for the objective: "
                f"{objective}"
            ),
        )

    @staticmethod
    def _is_transient_error(error: Exception) -> bool:
        """Return whether an error indicates a retryable provider failure."""
        status_code = getattr(error, "status_code", None)
        error_code = getattr(error, "code", None)
        message = str(error).upper()
        return (
            status_code in (429, 503)
            or error_code in (429, 503)
            or "UNAVAILABLE" in message
            or "RESOURCE_EXHAUSTED" in message
        )