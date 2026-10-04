# Evaluation Methodology

The evaluation framework rigorously measures whether an agent-selected configuration policy outperforms a deterministic, static baseline without making subjective claims about intelligence.

### Experimental Setup
We evaluate performance on three standard classification datasets from scikit-learn:
- Iris
- Breast Cancer
- Wine

### Baseline
The baseline strategy represents a standard grid-search approach. It deterministically runs through the configuration catalog using an interleaved pattern (`lr-default`, `rf-default`, `gb-default`, etc.) to guarantee broad coverage across model families.

### Agent
The agent strategy uses an adaptive selection policy. An LLM-driven planner receives the dataset profile and the history of previously evaluated configurations, and dynamically chooses the next configuration from the catalog based on previous metrics.

### Scripted Strategy
A deterministic scripted strategy (`rf-deep`, `gb-slow`, `lr-strong-reg`) exists purely to validate the underlying benchmark calculation engine, proving it can correctly track independent selection paths and progression differences.

### Search Space
To ensure fair comparison and prevent LLM hallucination, the search space is strictly bounded to 9 pre-defined, controlled configurations. Both the baseline and the agent must select their experiments exclusively from this catalog.

### Metrics
The primary execution metric is model **Accuracy** calculated via 5-fold stratified cross-validation.

### Best-so-far
We evaluate strategies using a sequential `best-so-far` metric. At experiment *N*, the best-so-far score is the maximum accuracy achieved across all experiments from 1 to *N*. This metric isolates learning efficiency: a better adaptive policy will increase its best-so-far curve earlier in the budget.

### experiments_to_reach_baseline_best
This metric counts how many iterations the agent required to reach or exceed the absolute highest score found by the baseline. It quantifies decision efficiency. If the agent achieves the baseline's best score in fewer steps, it proves the adaptive selection policy is effectively navigating the search space.

### Development Fallback Results
Currently, the recorded evaluation results (`evaluation_results.json`) reflect a "fallback" provider mode. This fallback intentionally mimics the baseline selection policy. These results merely validate that the benchmarking code works end-to-end; they do not measure LLM reasoning.

### Interpretation
The benchmark automatically generates neutral interpretations (e.g., "Agent achieved a higher best score than the baseline"). It mathematically compares scores and convergence speed without applying subjective labels like "smarter" or "intelligent".

### Limitations
- The dataset pool is limited to three small, clean, public classification datasets.
- The configuration search space is intentionally constrained to nine options.
- The task scope is classification-only.
- The results do not establish or imply general intelligence.

### Future Gemini Experiment
A full evaluation using the Gemini model is pending API quota availability. When executed, it will provide the final measurements of how effectively the Gemini LLM can act as an autonomous ML experiment planner.
