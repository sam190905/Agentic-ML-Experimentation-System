import sys
from pathlib import Path

import pandas as pd
from sklearn.datasets import load_iris

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent.planner import ExperimentPlanner
from app.profiler.dataset_profiler import DatasetProfiler


def main() -> None:
    iris = load_iris()
    data = pd.DataFrame(
        iris.data,
        columns=[
            "sepal_length",
            "sepal_width",
            "petal_length",
            "petal_width",
        ],
    )
    data["target"] = iris.target

    dataset_profile = DatasetProfiler().profile(data, target_column="target")
    decision = ExperimentPlanner().plan(
        objective="Classify iris species and maximize validation accuracy.",
        dataset_profile=dataset_profile,
        experiment_history=[],
    )

    print(f"Selected model: {decision.model}")
    print(f"Preprocessing: {decision.preprocessing}")
    print(f"Hyperparameters: {decision.hyperparameters}")
    print(f"Evaluation metric: {decision.evaluation_metric}")
    print(f"Reason: {decision.reason}")


if __name__ == "__main__":
    main()
