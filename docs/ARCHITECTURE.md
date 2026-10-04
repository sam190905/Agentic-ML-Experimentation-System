# System Architecture

The Agentic ML Experimentation System strictly separates responsibilities into distinct architectural layers.

## 1. Frontend
- **Responsibility:** Present experiment setup forms and rich result visualizations.
- **Input:** User objectives, budget, target column selection.
- **Output:** Rendered charts, trace history, best models, planning reasons.
- **Why it exists:** Provides an interactive interface for humans to easily monitor and interpret the agent's work.

## 2. FastAPI
- **Responsibility:** Act as the HTTP boundary and handle structured request/response validation.
- **Input:** JSON payload from the frontend.
- **Output:** Pydantic-validated JSON responses.
- **Why it exists:** Provides a robust, typed web server that isolates internal services from network concerns.

## 3. Service Layer
- **Responsibility:** Orchestrate the high-level workflow.
- **Input:** Validated API requests.
- **Output:** Final aggregated report dictionaries.
- **Why it exists:** Unifies the LangGraph invocation and the Report Generator without leaking business logic into the API routes.

## 4. LangGraph
- **Responsibility:** Manage the stateful, iterative loop of the experimentation process.
- **Input:** Initial `AgentState`.
- **Output:** Final `AgentState` containing populated history.
- **Why it exists:** Provides reliable orchestration, state management, and clear node transitions for the agentic feedback loop.

## 5. Dataset Profiler
- **Responsibility:** Analyze the raw tabular data.
- **Input:** Raw pandas DataFrame.
- **Output:** Statistical summary (rows, columns, classes, missing values).
- **Why it exists:** LLMs cannot natively compute statistics over raw CSVs; they need condensed, deterministic metadata to reason effectively.

## 6. Planner
- **Responsibility:** Decide the next experiment configuration based on history.
- **Input:** Dataset profile, objective, and past experiment history.
- **Output:** An `AgentDecision` containing a `config_id` and a `reason`.
- **Why it exists:** Isolates the non-deterministic LLM reasoning step from the deterministic execution environment.

## 7. Configuration Catalog
- **Responsibility:** Define the absolute bounds of the search space.
- **Input:** A requested `config_id`.
- **Output:** A fully hydrated `ExperimentConfig`.
- **Why it exists:** Prevents the LLM from hallucinating unsupported models or invalid hyperparameters.

## 8. Executor
- **Responsibility:** Run the ML pipeline.
- **Input:** `ExperimentConfig` and a pandas DataFrame.
- **Output:** `ExperimentResult` containing metrics (e.g., CV accuracy).
- **Why it exists:** Ensures mathematically sound, rigorous, and reproducible ML training and validation using scikit-learn.

## 9. Memory
- **Responsibility:** Persist experiments across sessions.
- **Input:** `ExperimentConfig` and `ExperimentResult`.
- **Output:** Saved database records.
- **Why it exists:** Provides durability and allows reviewing historical traces without re-running costly LLM inferences.

## 10. Report Generator
- **Responsibility:** Summarize the completed LangGraph state into a presentable format.
- **Input:** Final `experiment_history`.
- **Output:** Aggregated summary and best-experiment identification.
- **Why it exists:** Transforms raw iteration logs into actionable insights for the API/frontend to consume.

## 11. Evaluation Framework
- **Responsibility:** Compare different experiment selection strategies (e.g., Baseline vs. Agent).
- **Input:** Dataset, strategy definitions.
- **Output:** Objective metrics (`final_score_difference`, `experiments_to_reach_baseline_best`).
- **Why it exists:** Enables scientific, reproducible comparisons to prove the utility and efficiency of LLM-driven planning.
