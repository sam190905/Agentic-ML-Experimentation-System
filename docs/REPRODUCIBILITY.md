# Reproducibility Checklist

To ensure scientific integrity and reliable debugging, the evaluation framework and its experiments can be perfectly reproduced by following these environmental constraints.

## Python Version
- The project has been tested with Python 3.10+

## Dependency Installation
Dependencies are specified in `requirements.txt`:
- `pandas`
- `numpy`
- `scikit-learn`
- `python-dotenv`
- `pydantic`
- `langgraph`
- `langchain-openai`
- `langchain-google-genai`
- `fastapi`
- `uvicorn`
- `python-multipart`

Install them in a virtual environment via `uv`:
```bash
uv venv
uv pip install -r requirements.txt
```

## Environment Variables
Create a `.env` file containing the active provider:
```env
LLM_PROVIDER=fallback
# Add GEMINI_API_KEY when running the Gemini agent
```

## Random Seeds
All dataset splits and machine learning models enforce a deterministic `random_state=42` internal to their evaluation configurations.

## Evaluation Datasets
The benchmark runs against three standard scikit-learn datasets:
1. `load_iris()`
2. `load_breast_cancer()`
3. `load_wine()`

## Commands

**Test Suite (Validates system architecture):**
```bash
python -m pytest -q
```
*Note: Ensure all tests pass before running evaluations to confirm execution integrity.*

**Fallback Benchmark:**
```bash
python -m app.evaluation.runner --provider fallback
```

**Real Gemini Benchmark:**
```bash
python -m app.evaluation.runner --provider gemini
```

## Output Files
The evaluation runner programmatically generates and persists the following results in the `data/` directory:
1. **`data/evaluation_results.json`**: The complete raw trace containing every configuration, metric, dataset profile, and execution time.
2. **`data/benchmark_comparison.json`**: The structured JSON comparison quantifying the differences in convergence and scores between strategies.
3. **`data/evaluation_report.md`**: A human-readable Markdown summary representing the exact state of `benchmark_comparison.json`.

## How to Reproduce Fallback Results
To reproduce the exact baseline and fallback findings documented in this repository:
1. Guarantee `LLM_PROVIDER=fallback` is set.
2. Ensure you have not modified `app/experimentation/catalog.py` (any modification to the catalog alters the possible experiment space).
3. Execute `python -m app.evaluation.runner --provider fallback`.
4. Inspect `data/evaluation_report.md`. The fallback results will mirror the baseline exactly by design.
