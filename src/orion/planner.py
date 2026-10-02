from __future__ import annotations

import re
from typing import ClassVar, Protocol

from .models import PlanStep


class Planner(Protocol):
    def plan(self, task: str) -> list[PlanStep]: ...


class RulePlanner:
    """Deterministic planner used for reproducible local evaluation."""

    _PATTERNS: ClassVar[dict[str, re.Pattern[str]]] = {
        "add": re.compile(
            r"^\s*add\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*$",
            re.IGNORECASE,
        ),
        "multiply": re.compile(
            r"^\s*multiply\s+(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*$",
            re.IGNORECASE,
        ),
        "list_files": re.compile(r"^\s*list\s+files\s*$", re.IGNORECASE),
        "read_text": re.compile(r"^\s*read\s+(.+?)\s*$", re.IGNORECASE),
    }

    def plan(self, task: str) -> list[PlanStep]:
        for operation, pattern in self._PATTERNS.items():
            match = pattern.match(task)
            if not match:
                continue

            if operation in {"add", "multiply"}:
                return [
                    PlanStep(
                        server="calculator",
                        tool=operation,
                        arguments={
                            "a": float(match.group(1)),
                            "b": float(match.group(2)),
                        },
                    )
                ]

            if operation == "list_files":
                return [
                    PlanStep(
                        server="filesystem",
                        tool="list_files",
                        arguments={},
                    )
                ]

            return [
                PlanStep(
                    server="filesystem",
                    tool="read_text",
                    arguments={"path": match.group(1)},
                )
            ]

        raise ValueError(
            "unsupported task; use 'add A B', 'multiply A B', "
            "'list files', or 'read PATH'"
        )
