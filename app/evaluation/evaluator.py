"""Evaluator for comparing strategies."""

import os
from typing import Any

import pandas as pd

from app.evaluation.baseline import BaselineStrategy
from app.evaluation.schemas import StrategyResult, AggregateEvaluationResult, ExperimentStepResult
from app.schemas.experiment import ExperimentConfig, ExperimentResult
from app.services.experiment_service import ExperimentService


from app.evaluation.scripted import ScriptedStrategy

class Evaluator:
    def __init__(self, provider: str = "fallback"):
        self.provider = provider

    def evaluate_strategy(
        self,
        strategy_name: str,
        dataset_name: str,
        data: pd.DataFrame,
        target_column: str,
        objective: str,
        max_experiments: int = 3
    ) -> StrategyResult:
        
        if strategy_name == "baseline":
            history = BaselineStrategy().run(data, target_column, max_experiments)
        elif strategy_name == "scripted":
            history = ScriptedStrategy().run(data, target_column, max_experiments)
        elif strategy_name == "agent":
            original_provider = os.getenv("LLM_PROVIDER")
            os.environ["LLM_PROVIDER"] = self.provider
            try:
                response = ExperimentService().run(
                    data=data,
                    objective=objective,
                    target_column=target_column,
                    max_experiments=max_experiments
                )
                
                history = [
                    (
                        ExperimentConfig.model_validate(exp["configuration"]),
                        ExperimentResult.model_validate(exp["result"])
                    )
                    for exp in response["experiments"]
                ]
            except Exception as e:
                history = []
                # Fallback to catching the error, inferring failure_type
                failure_type = "execution"
                if isinstance(e, ValueError) and "Invalid config_id" in str(e):
                    failure_type = "planner"
                elif "validation" in str(e).lower() or "planner" in str(e).lower():
                    failure_type = "planner"
                elif "503" in str(e) or "429" in str(e) or "exhausted" in str(e).lower():
                    failure_type = "provider"
                
                # Append a fake history entry so metrics picks it up as a failed experiment
                config = ExperimentConfig(
                    experiment_id="failed-run",
                    config_id="unknown",
                    task_type="classification",
                    target_column=target_column,
                    model="unknown",
                    preprocessing=[],
                    hyperparameters={},
                    evaluation_metric="accuracy"
                )
                res = ExperimentResult(
                    experiment_id="failed-run",
                    status="failed",
                    metrics={},
                    training_time_seconds=0.0,
                    observations=[str(e)]
                )
                # Hack: Attach failure_type onto the result observations or similar,
                # actually _calculate_metrics can just look at result.status
                # But wait, ExperimentResult doesn't have failure_type. We can add it.
                # I'll just rely on the reporter knowing it from the step.
                res.status = "failed"
                history.append((config, res))
                
                # we'll inject failure_type later or add it directly in _calculate_metrics
            finally:
                if original_provider is not None:
                    os.environ["LLM_PROVIDER"] = original_provider
                else:
                    del os.environ["LLM_PROVIDER"]
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")

        return self._calculate_metrics(
            dataset_name=dataset_name,
            strategy_name=strategy_name,
            history=history
        )

    def _calculate_metrics(
        self,
        dataset_name: str,
        strategy_name: str,
        history: list[tuple[ExperimentConfig, ExperimentResult]]
    ) -> StrategyResult:
        successful_experiments = [h for h in history if h[1].status == "success"]
        
        first_score = None
        best_score = None
        best_model = None
        improvement = None
        total_time = sum(h[1].training_time_seconds for h in history)
        failed_count = sum(1 for h in history if h[1].status == "failed")
        
        steps = []
        best_scores_progression = {}
        current_best = None
        
        for i, (config, result) in enumerate(history):
            index = i + 1
            score = None
            if result.status == "success":
                metric_key = config.evaluation_metric
                score = result.metrics.get(metric_key)
                
            if score is not None:
                if current_best is None or score > current_best:
                    current_best = score
                    
            # Determine failure type if failed
            f_type = None
            if result.status == "failed":
                obs = " ".join(result.observations).lower()
                if "invalid config_id" in obs or "validation" in obs:
                    f_type = "planner"
                elif "503" in obs or "429" in obs or "exhausted" in obs:
                    f_type = "provider"
                else:
                    f_type = "execution"
                    
            steps.append(ExperimentStepResult(
                experiment_index=index,
                experiment_id=config.experiment_id,
                config_id=config.config_id,
                model=config.model,
                score=score,
                best_so_far=current_best,
                training_time_seconds=result.training_time_seconds,
                status=result.status,
                failure_type=f_type
            ))
            best_scores_progression[index] = current_best

        if successful_experiments:
            first_metric_key = successful_experiments[0][0].evaluation_metric
            first_score = successful_experiments[0][1].metrics.get(first_metric_key)
            
            best_exp = max(
                successful_experiments,
                key=lambda item: item[1].metrics.get(item[0].evaluation_metric, -float('inf'))
            )
            best_score = best_exp[1].metrics.get(best_exp[0].evaluation_metric)
            best_model = best_exp[0].model
            
            if first_score is not None and best_score is not None:
                improvement = best_score - first_score

        return StrategyResult(
            dataset_name=dataset_name,
            strategy=strategy_name,
            provider="none" if strategy_name == "baseline" else self.provider,
            experiments_run=len(history),
            first_experiment_score=first_score,
            best_score=best_score,
            best_model=best_model,
            improvement_from_first=improvement,
            total_training_time_seconds=total_time,
            failed_experiments=failed_count,
            experiment_history=history,
            steps=steps,
            best_scores_progression=best_scores_progression
        )
