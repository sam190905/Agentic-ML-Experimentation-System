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
        from app.experimentation.catalog import CATALOG, get_baseline_ordering

        history = [
            {
                "config_id": config.config_id,
                "result": result.model_dump(),
            }
            for config, result in experiment_history
        ]
        if self.provider == "fallback":
            return self._fallback_decision(objective, experiment_history)

        catalog_str = "\n".join(
            f'- config_id: "{entry.config_id}" | Model: {entry.model} | Hyperparameters: {entry.hyperparameters}'
            for entry in CATALOG
        )

        prompt = f"""
You are selecting the next machine learning experiment for an experimentation system.

Analyze the dataset profile, consider the user objective, and inspect the previous
experiment results. Avoid repeating an identical configuration (do not reuse a config_id that is in the history).
Choose one supported experiment config_id and explain why it was selected.

Available experiment configurations:
{catalog_str}

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
                decision = structured_model.invoke(prompt)
                # Validation is handled upstream in graph.py, 
                # but if we wanted to validate here we could.
                return decision
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
        from app.experimentation.catalog import get_baseline_ordering
        
        tried_config_ids = {config.config_id for config, _ in experiment_history}
        ordering = get_baseline_ordering()
        
        for entry in ordering:
            if entry.config_id not in tried_config_ids:
                return AgentDecision(
                    config_id=entry.config_id,
                    reason=(
                        "Deterministic development/demo fallback selected "
                        f"{entry.config_id} because it has not been tried yet for "
                        f"the objective: {objective}"
                    ),
                )
                
        # If all tried, just repeat the first one
        entry = ordering[0]
        return AgentDecision(
            config_id=entry.config_id,
            reason=(
                "Deterministic development/demo fallback selected "
                f"{entry.config_id} because all configurations have already been tried for the objective: "
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