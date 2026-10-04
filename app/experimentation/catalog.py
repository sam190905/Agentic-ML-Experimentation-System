"""Centralized catalog of supported experiment configurations."""

from typing import Any
from pydantic import BaseModel


class CatalogEntry(BaseModel):
    """A controlled experiment configuration."""
    config_id: str
    model: str
    preprocessing: list[str]
    hyperparameters: dict[str, Any]
    evaluation_metric: str = "accuracy"


CATALOG = [
    # Logistic Regression
    CatalogEntry(
        config_id="lr-default",
        model="logistic_regression",
        preprocessing=["standard_scaler"],
        hyperparameters={"C": 1.0, "max_iter": 200, "solver": "lbfgs"}
    ),
    CatalogEntry(
        config_id="lr-strong-reg",
        model="logistic_regression",
        preprocessing=["standard_scaler"],
        hyperparameters={"C": 0.1, "max_iter": 200, "solver": "lbfgs"}
    ),
    CatalogEntry(
        config_id="lr-weak-reg",
        model="logistic_regression",
        preprocessing=["standard_scaler"],
        hyperparameters={"C": 10.0, "max_iter": 200, "solver": "lbfgs"}
    ),
    
    # Random Forest
    CatalogEntry(
        config_id="rf-default",
        model="random_forest",
        preprocessing=["standard_scaler"],
        hyperparameters={"n_estimators": 100, "max_depth": None, "random_state": 42, "n_jobs": -1}
    ),
    CatalogEntry(
        config_id="rf-shallow",
        model="random_forest",
        preprocessing=["standard_scaler"],
        hyperparameters={"n_estimators": 200, "max_depth": 5, "random_state": 42, "n_jobs": -1}
    ),
    CatalogEntry(
        config_id="rf-deep",
        model="random_forest",
        preprocessing=["standard_scaler"],
        hyperparameters={"n_estimators": 200, "max_depth": None, "random_state": 42, "n_jobs": -1}
    ),
    
    # Gradient Boosting
    CatalogEntry(
        config_id="gb-default",
        model="gradient_boosting",
        preprocessing=["standard_scaler"],
        hyperparameters={"n_estimators": 100, "learning_rate": 0.1, "random_state": 42}
    ),
    CatalogEntry(
        config_id="gb-slow",
        model="gradient_boosting",
        preprocessing=["standard_scaler"],
        hyperparameters={"n_estimators": 200, "learning_rate": 0.05, "random_state": 42}
    ),
    CatalogEntry(
        config_id="gb-fast",
        model="gradient_boosting",
        preprocessing=["standard_scaler"],
        hyperparameters={"n_estimators": 100, "learning_rate": 0.2, "random_state": 42}
    ),
]


def get_catalog_entry(config_id: str) -> CatalogEntry:
    """Retrieve a catalog entry by ID."""
    for entry in CATALOG:
        if entry.config_id == config_id:
            return entry
    raise ValueError(f"Invalid config_id: '{config_id}' is not in the configuration catalog.")


def get_baseline_ordering() -> list[CatalogEntry]:
    """Returns an interleaved baseline ordering."""
    return [
        get_catalog_entry("lr-default"),
        get_catalog_entry("rf-default"),
        get_catalog_entry("gb-default"),
        get_catalog_entry("lr-strong-reg"),
        get_catalog_entry("rf-shallow"),
        get_catalog_entry("gb-slow"),
        get_catalog_entry("lr-weak-reg"),
        get_catalog_entry("rf-deep"),
        get_catalog_entry("gb-fast"),
    ]
