from __future__ import annotations

from .models import AgentResult
from .planner import Planner
from .runtime import MCPAgentRuntime


class Agent:
    """Plan -> authorize -> execute -> trace."""

    def __init__(self, planner: Planner, runtime: MCPAgentRuntime) -> None:
        self.planner = planner
        self.runtime = runtime

    async def run(self, task: str) -> AgentResult:
        return await self.runtime.execute(task, self.planner.plan(task))
