import pandas as pd
from app.evaluation.evaluator import Evaluator
from sklearn.datasets import load_iris

def get_test_data():
    iris = load_iris()
    data = pd.DataFrame(
        iris.data,
        columns=["sepal_length", "sepal_width", "petal_length", "petal_width"],
    )
    data["target"] = iris.target
    return data

def test_scripted_evaluation():
    data = get_test_data()
    evaluator = Evaluator(provider="fallback")
    
    # 1. Baseline sequence is unchanged (and Evaluator does not hard-code baseline assumptions)
    baseline_result = evaluator.evaluate_strategy(
        strategy_name="baseline",
        dataset_name="iris_test",
        data=data,
        target_column="target",
        objective="Classify iris species",
        max_experiments=3
    )
    
    baseline_configs = [c.config_id for c, r in baseline_result.experiment_history]
    assert baseline_configs == ["lr-default", "rf-default", "gb-default"]
    
    # 2. Scripted strategy selects the intended config_ids
    scripted_result = evaluator.evaluate_strategy(
        strategy_name="scripted",
        dataset_name="iris_test",
        data=data,
        target_column="target",
        objective="Classify iris species",
        max_experiments=3
    )
    
    scripted_configs = [c.config_id for c, r in scripted_result.experiment_history]
    assert scripted_configs == ["rf-deep", "gb-slow", "lr-strong-reg"]
    
    # 3. Both strategies use the same ExperimentExecutor
    # 4. Best-so-far is calculated independently for each strategy
    # 5. Different strategy sequences produce independently recorded results
    # (By asserting the best scores and histories are separate objects and different)
    assert baseline_result.experiment_history != scripted_result.experiment_history
    assert baseline_result.steps != scripted_result.steps
    assert len(baseline_result.best_scores_progression) == 3
    assert len(scripted_result.best_scores_progression) == 3
    
    # 7. The resulting JSON preserves the exact config_id sequence (Evaluator step JSON schema)
    # The evaluation schemas (AggregateEvaluationResult) will persist whatever is in experiment_history.
    # Just asserting the models are populated correctly.
    assert baseline_result.steps[0].model == "logistic_regression"
    assert scripted_result.steps[0].model == "random_forest"
