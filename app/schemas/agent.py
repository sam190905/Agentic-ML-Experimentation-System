"""Pydantic schemas for agent decisions."""

from typing import Literal

from pydantic import BaseModel


class AgentDecision(BaseModel):
    """Experiment configuration selected by the planning model."""

    config_id: str
    reason: str