# Agentic ML Experimentation System

An LLM-based system for analyzing tabular machine learning problems, selecting controlled scikit-learn experiments, evaluating results, maintaining experiment history, and iteratively choosing the next experiment.

## Architecture

The planned system will connect these stages:

1. Problem analysis for a tabular ML task.
2. Experiment selection through an agentic orchestration layer.
3. Controlled execution with scikit-learn tools.
4. Evaluation and persistent experiment history.
5. Iterative selection of the next experiment using the observed results.

## Development Phases

- **Phase 0:** Project foundation and environment setup.
- **Phase 1:** Controlled ML experimentation components.
- **Phase 2:** Agent orchestration and LLM integration.
- **Phase 3:** Experiment history, retrieval, and persistence.
- **Phase 4:** Evaluation, interface, and end-to-end refinement.

Only the Phase 0 foundation is currently established.

## Technology Stack

- Python
- pandas and NumPy for tabular data handling
- scikit-learn for controlled ML experiments
- Pydantic for typed data models
- python-dotenv for environment configuration
- Planned integrations: an LLM, LangGraph, retrieval, persistence, and a user interface