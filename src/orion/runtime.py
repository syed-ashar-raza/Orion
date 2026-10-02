from __future__ import annotations

from typing import Any

from mcp import Client
from mcp.shared.exceptions import MCPError

from .models import AgentResult, Decision, ExecutionRecord, PlanStep, ToolRef
from .policy import ToolPolicy


class MCPAgentRuntime:
    """MCP discovery, explicit authorization, execution, and tracing."""

    def __init__(self, servers: dict[str, Any], policy: ToolPolicy) -> None:
        self.servers = servers
        self.policy = policy

    async def discover_tools(self) -> list[ToolRef]:
        discovered: list[ToolRef] = []
        for server_name, server in self.servers.items():
            async with Client(server) as client:
                result = await client.list_tools()
                for tool in result.tools:
                    discovered.append(ToolRef(server=server_name, name=tool.name, description=tool.description, input_schema=tool.input_schema))
        return discovered

    async def execute(self, task: str, steps: list[PlanStep]) -> AgentResult:
        records: list[ExecutionRecord] = []
        outputs: list[Any] = []
        for step in steps:
            decision = self.policy.authorize(step.server, step.tool, step.arguments)
            if decision is Decision.DENY:
                records.append(ExecutionRecord(server=step.server, tool=step.tool, decision=decision, success=False, error="tool denied by policy"))
                continue
            server = self.servers.get(step.server)
            if server is None:
                records.append(ExecutionRecord(server=step.server, tool=step.tool, decision=Decision.DENY, success=False, error="unknown MCP server"))
                continue
            try:
                async with Client(server) as client:
                    result = await client.call_tool(step.tool, arguments=step.arguments)
            except MCPError as exc:
                records.append(ExecutionRecord(server=step.server, tool=step.tool, decision=decision, success=False, error=str(exc)))
                continue
            if result.is_error:
                records.append(ExecutionRecord(server=step.server, tool=step.tool, decision=decision, success=False, error=self._text(result)))
                continue
            outputs.append(result.structured_content if result.structured_content is not None else self._text(result))
            records.append(ExecutionRecord(server=step.server, tool=step.tool, decision=decision, success=True))
        return AgentResult(task=task, steps=steps, records=records, outputs=outputs)

    @staticmethod
    def _text(result: Any) -> str:
        return "\n".join(text for block in result.content if (text := getattr(block, "text", None)) is not None)
