"""Service facade for running and reporting ML experiments."""

from typing import Any
from uuid import uuid4

import pandas as pd

from app.agent.graph import graph
from app.agent.state import AgentState
from app.reporting.report_generator import ReportGenerator


class ExperimentService:
    """Run the complete experimentation graph and build its final report."""

    def run(
        self,
        data: pd.DataFrame,
        objective: str,
        target_column: str,
        max_experiments: int = 3,
    ) -> dict[str, Any]:
        """Execute the graph once and return its report sections."""
        run_id = str(uuid4())
        initial_state: AgentState = {
            "data": data,
            "run_id": run_id,
            "objective": objective,
            "target_column": target_column,
            "dataset_profile": None,
            "current_experiment": None,
            "latest_result": None,
            "experiment_history": [],
            "experiment_count": 0,
            "max_experiments": max_experiments,
        }
        final_state = graph.invoke(initial_state)
        dataset_profile = final_state["dataset_profile"]
        if dataset_profile is None:
            raise ValueError("Graph did not produce a dataset profile")

        experiment_history = final_state["experiment_history"]
        report = ReportGenerator(
            objective=objective,
            dataset_profile=dataset_profile,
            experiment_history=experiment_history,
        ).generate()

        return {
            "run_id": run_id,
            "dataset_profile": report["dataset_summary"],
            "experiments": report["experiments"],
            "best_experiment": report["best_experiment"],
            "report": report,
        }
