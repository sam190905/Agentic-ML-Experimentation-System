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
        self.model_name = os.getenv("LLM_MODEL", "gemini-2.5-flash")
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