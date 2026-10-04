import pytest
import pandas as pd
from app.experimentation.catalog import CATALOG, get_catalog_entry, get_baseline_ordering
from app.schemas.experiment import ExperimentConfig
from app.experimentation.executor import ExperimentExecutor

def test_catalog_validity():
    """1. Configuration catalog validity"""
    assert len(CATALOG) == 9
    for entry in CATALOG:
        assert entry.config_id
        assert entry.model in {"logistic_regression", "random_forest", "gradient_boosting"}

def test_every_catalog_configuration_executes_successfully():
    """2. Every catalog configuration executes successfully"""
    # Create a simple dataset
    df = pd.DataFrame({
        "feature1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "feature2": [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        "target": [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    })
    executor = ExperimentExecutor()
    for entry in CATALOG:
        config = ExperimentConfig(
            experiment_id=f"test-{entry.config_id}",
            config_id=entry.config_id,
            task_type="classification",
            target_column="target",
            model=entry.model,
            preprocessing=entry.preprocessing,
            hyperparameters=entry.hyperparameters,
            evaluation_metric=entry.evaluation_metric,
        )
        result = executor.execute(df, config)
        assert result.status == "success"

def test_invalid_config_id_rejection():
    """3 & 4. Invalid config_id rejection (covers model & hyperparameter rejection)"""
    with pytest.raises(ValueError, match="Invalid config_id"):
        get_catalog_entry("invalid-id")

def test_configuration_identity():
    """5. Configuration identity"""
    ids = [entry.config_id for entry in CATALOG]
    assert len(ids) == len(set(ids))

def test_baseline_uses_same_catalog():
    """8. Baseline uses the same catalog"""
    ordering = get_baseline_ordering()
    assert len(ordering) == len(CATALOG)
    for entry in ordering:
        assert get_catalog_entry(entry.config_id) == entry
