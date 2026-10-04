import pytest
from app.evaluation.schemas import (
    StrategyResult,
    ExperimentStepResult,
    BenchmarkComparison,
    BenchmarkReport
)
from app.evaluation.reporter import Reporter

def get_dummy_strategy_result(
    strategy: str, best_score: float | None, scores: list[float], failures: list[str] = None
) -> StrategyResult:
    steps = []
    for i, score in enumerate(scores):
        f_type = None
        if failures and i < len(failures) and failures[i]:
            f_type = failures[i]
            status = "failed"
        else:
            status = "success"
            
        steps.append(ExperimentStepResult(
            experiment_index=i+1,
            experiment_id=f"{strategy}-{i}",
            config_id=f"config-{i}",
            model="dummy_model",
            score=score,
            best_so_far=max([s for s in scores[:i+1] if s is not None]) if any(s is not None for s in scores[:i+1]) else None,
            training_time_seconds=1.0,
            status=status,
            failure_type=f_type
        ))
        
    return StrategyResult(
        dataset_name="dummy",
        strategy=strategy,
        provider="fallback",
        experiments_run=len(scores),
        first_experiment_score=scores[0] if scores else None,
        best_score=best_score,
        best_model="dummy_model",
        improvement_from_first=(best_score - scores[0]) if best_score and scores and scores[0] else None,
        total_training_time_seconds=float(len(scores)),
        failed_experiments=len([f for f in (failures or []) if f]),
        experiment_history=[],
        steps=steps,
        best_scores_progression={i+1: s for i, s in enumerate(scores)}
    )

def test_reporter_higher_score():
    baseline = get_dummy_strategy_result("baseline", 0.8, [0.8])
    agent = get_dummy_strategy_result("agent", 0.9, [0.9])
    
    comp = Reporter.compare("dummy", baseline, agent)
    assert comp.final_score_difference == pytest.approx(0.1)
    assert comp.interpretation == "Agent achieved a higher best score than the baseline."

def test_reporter_lower_score():
    baseline = get_dummy_strategy_result("baseline", 0.9, [0.9])
    agent = get_dummy_strategy_result("agent", 0.8, [0.8])
    
    comp = Reporter.compare("dummy", baseline, agent)
    assert comp.final_score_difference == pytest.approx(-0.1)
    assert comp.interpretation == "Agent achieved a lower best score than the baseline."

def test_reporter_tied_same_experiments():
    baseline = get_dummy_strategy_result("baseline", 0.9, [0.9])
    agent = get_dummy_strategy_result("agent", 0.9, [0.9])
    
    comp = Reporter.compare("dummy", baseline, agent)
    assert comp.interpretation == "Agent matched the baseline final score."

def test_reporter_tied_fewer_experiments():
    baseline = get_dummy_strategy_result("baseline", 0.9, [0.8, 0.9])
    agent = get_dummy_strategy_result("agent", 0.9, [0.9, 0.9])
    
    comp = Reporter.compare("dummy", baseline, agent)
    assert comp.interpretation == "Agent reached the baseline score in fewer experiments."

def test_reporter_tied_more_experiments():
    baseline = get_dummy_strategy_result("baseline", 0.9, [0.9, 0.9])
    agent = get_dummy_strategy_result("agent", 0.9, [0.8, 0.9])
    
    comp = Reporter.compare("dummy", baseline, agent)
    assert comp.interpretation == "Agent took more experiments to reach the same best score."
    assert comp.experiments_to_reach_baseline_best == 2

def test_reporter_failures_recorded():
    baseline = get_dummy_strategy_result("baseline", 0.9, [0.9])
    agent = get_dummy_strategy_result("agent", 0.9, [None, 0.9], failures=["planner", None])
    
    comp = Reporter.compare("dummy", baseline, agent)
    assert len(comp.agent_trace) == 2
    assert comp.agent_trace[0].failure_type == "planner"

def test_reporter_markdown_generation():
    baseline = get_dummy_strategy_result("baseline", 0.9, [0.9])
    agent = get_dummy_strategy_result("agent", 0.9, [0.9])
    comp = Reporter.compare("dummy", baseline, agent)
    
    md = Reporter.generate_markdown(BenchmarkReport(comparisons=[comp]))
    assert "Agentic ML Experimentation Benchmark" in md
    assert "Agent matched the baseline final score." in md
    assert "Dummy" in md
