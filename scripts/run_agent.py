import sys
from pathlib import Path
from uuid import uuid4

import pandas as pd
from sklearn.datasets import load_iris

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.agent.graph import graph


def build_iris_data() -> pd.DataFrame:
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
    return data


def main() -> None:
    initial_state = {
        "data": build_iris_data(),
        "run_id": f"run-{uuid4()}",
        "objective": "Classify iris species and maximize validation accuracy.",
        "target_column": "target",
        "dataset_profile": None,
        "current_experiment": None,
        "latest_result": None,
        "experiment_history": [],
        "experiment_count": 0,
        "max_experiments": 3,
    }

    result = graph.invoke(initial_state)
    dataset_profile = result["dataset_profile"]
    history = result["experiment_history"]

    print("Dataset profile:")
    print(dataset_profile.model_dump() if dataset_profile else "Unavailable")
    print(f"\nNumber of experiments executed: {result['experiment_count']}")

    for experiment, experiment_result in history:
        print(f"\nExperiment: {experiment.experiment_id}")
        print(f"Model: {experiment.model}")
        print(f"Preprocessing: {experiment.preprocessing}")
        print(f"Hyperparameters: {experiment.hyperparameters}")
        print(f"Evaluation metric: {experiment.evaluation_metric}")
        print(f"Resulting metric: {experiment_result.metrics}")
        print(
            "Reason: unavailable; planner reasoning is not retained "
            "in the current graph state."
        )

    successful_experiments = [
        (experiment, experiment_result)
        for experiment, experiment_result in history
        if experiment_result.status == "success"
        and experiment_result.metrics
    ]
    if successful_experiments:
        best_experiment, best_result = max(
            successful_experiments,
            key=lambda item: item[1].metrics.get("accuracy", float("-inf")),
        )
        print("\nBest experiment:")
        print(f"Experiment ID: {best_experiment.experiment_id}")
        print(f"Model: {best_experiment.model}")
        print(f"Accuracy: {best_result.metrics['accuracy']}")
    else:
        print("\nBest experiment: unavailable")


if __name__ == "__main__":
    main()
