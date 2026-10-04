"""Generates benchmark comparisons and reports."""

from app.evaluation.schemas import (
    AgentTraceStep,
    BenchmarkComparison,
    BenchmarkReport,
    StrategyResult
)


class Reporter:
    @staticmethod
    def compare(
        dataset_name: str, baseline: StrategyResult, agent: StrategyResult
    ) -> BenchmarkComparison:

        # Calculate final score difference
        b_final = baseline.best_score
        a_final = agent.best_score
        final_diff = None
        if b_final is not None and a_final is not None:
            final_diff = a_final - b_final

        # Calculate best score difference at each step
        best_score_diff = {}
        for i in range(1, max(agent.experiments_run, baseline.experiments_run) + 1):
            b_val = baseline.best_scores_progression.get(i)
            a_val = agent.best_scores_progression.get(i)
            if b_val is not None and a_val is not None:
                best_score_diff[i] = a_val - b_val
            else:
                best_score_diff[i] = None

        # experiments_to_reach_baseline_best
        exp_reach = None
        if b_final is not None:
            for step in agent.steps:
                if step.best_so_far is not None and step.best_so_far >= b_final:
                    exp_reach = step.experiment_index
                    break

        # Trace
        trace = []
        for step in agent.steps:
            reason = None
            for config, res in agent.experiment_history:
                if config.experiment_id == step.experiment_id:
                    reason = config.planning_reason
                    break
            
            trace.append(AgentTraceStep(
                experiment_index=step.experiment_index,
                config_id=step.config_id if step.config_id else "unknown",
                model=step.model if step.model else "unknown",
                score=step.score,
                best_so_far=step.best_so_far,
                planning_reason=reason,
                failure_type=step.failure_type
            ))

        # Automatic Interpretation
        if b_final is None or a_final is None:
            interpretation = "Results were insufficient to determine a conclusion."
        elif final_diff > 1e-9:  # Float comparison
            interpretation = "Agent achieved a higher best score than the baseline."
        elif final_diff < -1e-9:
            interpretation = "Agent achieved a lower best score than the baseline."
        else:
            b_first = next((s.experiment_index for s in baseline.steps if s.best_so_far == b_final), None)
            a_first = next((s.experiment_index for s in agent.steps if s.best_so_far == a_final), None)
            
            if a_first is not None and b_first is not None:
                if a_first < b_first:
                    interpretation = "Agent reached the baseline score in fewer experiments."
                elif a_first > b_first:
                    interpretation = "Agent took more experiments to reach the same best score."
                else:
                    interpretation = "Agent matched the baseline final score."
            else:
                interpretation = "Agent matched the baseline final score."

        return BenchmarkComparison(
            dataset_name=dataset_name,
            baseline_result=baseline,
            agent_result=agent,
            final_score_difference=final_diff,
            best_score_difference_at_step=best_score_diff,
            experiments_to_reach_baseline_best=exp_reach,
            final_best_model_baseline=baseline.best_model,
            final_best_model_agent=agent.best_model,
            interpretation=interpretation,
            agent_trace=trace
        )

    @staticmethod
    def generate_markdown(report: BenchmarkReport) -> str:
        lines = [
            "# Agentic ML Experimentation Benchmark",
            "",
            "## Experimental Setup",
            "",
            "Datasets:",
        ]
        
        datasets = []
        for comp in report.comparisons:
            if comp.dataset_name not in datasets:
                datasets.append(comp.dataset_name)
                
        for ds in datasets:
            lines.append(f"- {ds.capitalize()}")
            
        lines.extend([
            "",
            "Strategies:",
            "- Baseline",
            "- Gemini Agent",
            "",
            "Search space:",
            "9 controlled configurations",
            "",
            "Metric:",
            "Accuracy",
            "",
            "Validation:",
            "5-fold stratified cross-validation",
            "",
            "## Results",
            "",
            "| Dataset | Strategy | After 1 | After 2 | After 3 | Final | Best Model | Improvement |",
            "|---------|----------|---------|---------|---------|-------|------------|-------------|"
        ])
        
        for comp in report.comparisons:
            ds = comp.dataset_name.capitalize()
            for strategy_name, s_res in [("Baseline", comp.baseline_result), ("Agent", comp.agent_result)]:
                a1 = f"{s_res.best_scores_progression.get(1):.4f}" if s_res.best_scores_progression.get(1) is not None else "N/A"
                a2 = f"{s_res.best_scores_progression.get(2):.4f}" if s_res.best_scores_progression.get(2) is not None else "N/A"
                a3 = f"{s_res.best_scores_progression.get(3):.4f}" if s_res.best_scores_progression.get(3) is not None else "N/A"
                final = f"{s_res.best_score:.4f}" if s_res.best_score is not None else "N/A"
                best_model = s_res.best_model if s_res.best_model else "N/A"
                imp = f"{s_res.improvement_from_first:+.4f}" if s_res.improvement_from_first is not None else "N/A"
                
                lines.append(f"| {ds} | {strategy_name} | {a1} | {a2} | {a3} | {final} | {best_model} | {imp} |")

        lines.extend([
            "",
            "## Agent Trace",
            ""
        ])

        for comp in report.comparisons:
            lines.extend([f"### {comp.dataset_name.capitalize()}", ""])
            for t in comp.agent_trace:
                score_str = f"{t.score:.4f}" if t.score is not None else "N/A"
                best_str = f"{t.best_so_far:.4f}" if t.best_so_far is not None else "N/A"
                reason = t.planning_reason if t.planning_reason else "N/A"
                lines.extend([
                    f"**Experiment {t.experiment_index}**",
                    f"- **Config ID:** {t.config_id}",
                    f"- **Model:** {t.model}",
                    f"- **Score:** {score_str}",
                    f"- **Best So Far:** {best_str}"
                ])
                if t.failure_type:
                    lines.append(f"- **Failure:** {t.failure_type}")
                lines.extend([
                    f"- **Planning Reason:** {reason}",
                    ""
                ])

        lines.extend([
            "## Comparison",
            ""
        ])
        
        for comp in report.comparisons:
            lines.extend([f"### {comp.dataset_name.capitalize()}", ""])
            fd = f"{comp.final_score_difference:+.4f}" if comp.final_score_difference is not None else "N/A"
            reach = str(comp.experiments_to_reach_baseline_best) if comp.experiments_to_reach_baseline_best is not None else "N/A"
            
            lines.extend([
                f"- **Final Score Difference:** {fd}",
                f"- **Experiments to Reach Baseline Best:** {reach}",
                ""
            ])

            failures = [t.failure_type for t in comp.agent_trace if t.failure_type is not None]
            if failures:
                lines.append(f"- **Failures:** {len(failures)} ({', '.join(failures)})")
            else:
                lines.append("- **Failures:** None")
            lines.append("")

        lines.extend([
            "## Interpretation",
            ""
        ])
        
        for comp in report.comparisons:
            lines.extend([
                f"**{comp.dataset_name.capitalize()}:**",
                comp.interpretation,
                ""
            ])

        lines.extend([
            "## Limitations",
            "",
            "- dataset size",
            "- limited configuration space",
            "- classification-only scope",
            "- LLM provider availability",
            "- benchmark does not prove general intelligence",
            ""
        ])

        return "\n".join(lines)
