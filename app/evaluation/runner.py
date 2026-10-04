"""Command-line runner for the evaluation framework."""

import argparse
from pathlib import Path

from app.evaluation.datasets import get_evaluation_datasets
from app.evaluation.evaluator import Evaluator
from app.evaluation.schemas import AggregateEvaluationResult


def run_evaluation(provider: str, strategies: list[str]) -> None:
    datasets = get_evaluation_datasets()
    evaluator = Evaluator(provider=provider)
    
    results = []
    
    print(f"{'Dataset':<15} {'Strategy':<12} {'After 1':<10} {'After 2':<10} {'After 3':<10} {'Final':<8} {'Best Model':<20} {'Improvement'}")
    print("-" * 105)
    
    for dataset_name, ds_info in datasets.items():
        for strategy in strategies:
            result = evaluator.evaluate_strategy(
                strategy_name=strategy,
                dataset_name=dataset_name,
                data=ds_info["data"],
                target_column=ds_info["target_column"],
                objective=ds_info["objective"],
                max_experiments=3
            )
            results.append(result)
            
            a1 = f"{result.best_scores_progression.get(1):.4f}" if result.best_scores_progression.get(1) is not None else "N/A"
            a2 = f"{result.best_scores_progression.get(2):.4f}" if result.best_scores_progression.get(2) is not None else "N/A"
            a3 = f"{result.best_scores_progression.get(3):.4f}" if result.best_scores_progression.get(3) is not None else "N/A"
            final = f"{result.best_score:.4f}" if result.best_score is not None else "N/A"
            best_model = result.best_model if result.best_model is not None else "N/A"
            improvement = f"{result.improvement_from_first:+.4f}" if result.improvement_from_first is not None else "N/A"
            
            print(f"{dataset_name.capitalize():<15} {strategy.capitalize():<12} {a1:<10} {a2:<10} {a3:<10} {final:<8} {best_model:<20} {improvement}")
            
    aggregate = AggregateEvaluationResult(evaluations=results)
    
    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    out_file = out_dir / "evaluation_results.json"
    
    with open(out_file, "w") as f:
        f.write(aggregate.model_dump_json(indent=2))
        
    print(f"\nSaved full evaluation results to {out_file}")

    print("\nInterpretation:")
    dataset_groups = {}
    for r in results:
        dataset_groups.setdefault(r.dataset_name, {})[r.strategy] = r
        
    # Build benchmark report if both baseline and agent are present
    from app.evaluation.reporter import Reporter
    from app.evaluation.schemas import BenchmarkReport
    
    comparisons = []
    
    for ds_name, grp in dataset_groups.items():
        baseline = grp.get("baseline")
        agent = grp.get("agent")
        
        if not baseline or not agent:
            continue
            
        comp = Reporter.compare(ds_name, baseline, agent)
        comparisons.append(comp)
        
        print(f"\n{ds_name.capitalize()}:")
        print(comp.interpretation)

    if comparisons:
        report = BenchmarkReport(comparisons=comparisons)
        
        comp_file = out_dir / "benchmark_comparison.json"
        with open(comp_file, "w") as f:
            f.write(report.model_dump_json(indent=2))
        print(f"Saved benchmark comparison to {comp_file}")
            
        md_file = out_dir / "evaluation_report.md"
        with open(md_file, "w") as f:
            f.write(Reporter.generate_markdown(report))
        print(f"Saved evaluation report to {md_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the agent evaluation benchmark.")
    parser.add_argument(
        "--provider",
        type=str,
        default="fallback",
        choices=["fallback", "gemini"],
        help="LLM provider for the agent strategy."
    )
    parser.add_argument(
        "--strategies",
        nargs="+",
        default=["baseline", "agent"],
        help="List of strategies to evaluate (e.g. baseline agent scripted)"
    )
    args = parser.parse_args()
    run_evaluation(args.provider, args.strategies)
