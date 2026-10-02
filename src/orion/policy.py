from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import Decision


@dataclass(frozen=True)
class ToolPolicy:
    allowed: dict[str, set[str]] = field(default_factory=dict)
    max_argument_bytes: int = 16_384

    def authorize(self, server: str, tool: str, arguments: dict[str, Any]) -> Decision:
        if tool not in self.allowed.get(server, set()):
            return Decision.DENY
        if len(str(arguments).encode("utf-8")) > self.max_argument_bytes:
            return Decision.DENY
        return Decision.ALLOW
