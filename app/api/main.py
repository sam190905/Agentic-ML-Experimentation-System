"""FastAPI endpoints for the ML experimentation service."""

import os
from io import BytesIO
import logging
from typing import Any

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.services.experiment_service import ExperimentService

logger = logging.getLogger(__name__)


def _get_cors_origins() -> list[str]:
    """Return the list of allowed CORS origins.

    When the CORS_ORIGINS environment variable is set, its
    comma-separated values are used as the explicit allowlist.
    When it is not set, localhost development defaults are returned.
    """
    cors_env = os.getenv("CORS_ORIGINS")
    if cors_env:
        return [origin.strip() for origin in cors_env.split(",") if origin.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


app = FastAPI(title="Agentic ML Experimentation System")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict[str, str]:
    """Return the API health status."""
    return {"status": "ok"}


@app.post("/api/experiments/run")
def run_experiment(
    file: UploadFile = File(...),
    objective: str = Form(...),
    target_column: str = Form(...),
    max_experiments: int = Form(3, ge=1),
) -> dict[str, Any]:
    """Run the experimentation service for an uploaded CSV dataset."""
    try:
        data = pd.read_csv(BytesIO(file.file.read()))
    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid CSV file: {error}",
        ) from error

    if target_column not in data.columns:
        raise HTTPException(
            status_code=400,
            detail=f"Target column '{target_column}' was not found",
        )

    try:
        return ExperimentService().run(
            data=data,
            objective=objective,
            target_column=target_column,
            max_experiments=max_experiments,
        )
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("Experiment execution failed")
        raise HTTPException(
            status_code=500,
            detail="Experiment execution failed",
        ) from error
