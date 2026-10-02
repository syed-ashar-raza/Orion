from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class Decision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"


class PlanStep(BaseModel):
    server: str
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class ToolRef(BaseModel):
    server: str
    name: str
    description: str | None = None
    input_schema: dict[str, Any] | None = None


class ExecutionRecord(BaseModel):
    server: str
    tool: str
    decision: Decision
    success: bool
    error: str | None = None


class AgentResult(BaseModel):
    task: str
    steps: list[PlanStep]
    records: list[ExecutionRecord]
    outputs: list[Any]
