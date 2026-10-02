import pytest
from mcp import Client

from orion.agent import Agent
from orion.models import Decision, PlanStep
from orion.planner import RulePlanner
from orion.policy import ToolPolicy
from orion.runtime import MCPAgentRuntime
from orion.servers.calculator import mcp as calculator_server
from orion.servers.filesystem import mcp as filesystem_server


@pytest.fixture
def runtime():
    return MCPAgentRuntime(
        {"calculator": calculator_server},
        ToolPolicy(allowed={"calculator": {"add", "multiply"}}),
    )


@pytest.mark.anyio
async def test_mcp_tool_discovery(runtime):
    tools = await runtime.discover_tools()
    assert {tool.name for tool in tools} == {"add", "multiply"}


@pytest.mark.anyio
async def test_direct_mcp_call():
    async with Client(calculator_server) as client:
        result = await client.call_tool("add", arguments={"a": 2, "b": 3})
    assert not result.is_error
    assert result.structured_content == {"result": 5.0}


@pytest.mark.anyio
async def test_agent_execution(runtime):
    result = await Agent(RulePlanner(), runtime).run("add 2 3")
    assert result.outputs == [{"result": 5.0}]
    assert result.records[0].success


@pytest.mark.anyio
async def test_policy_denies_unlisted_tool(runtime):
    result = await runtime.execute(
        "unauthorized",
        [PlanStep(server="calculator", tool="unknown", arguments={})],
    )
    assert result.records[0].decision is Decision.DENY
    assert not result.records[0].success


@pytest.mark.anyio
async def test_policy_denies_registered_but_unauthorized_tool():
    runtime = MCPAgentRuntime(
        {"calculator": calculator_server},
        ToolPolicy(allowed={"calculator": {"add"}}),
    )
    result = await runtime.execute(
        "unauthorized",
        [
            PlanStep(
                server="calculator",
                tool="multiply",
                arguments={"a": 2, "b": 3},
            )
        ],
    )
    assert result.records[0].decision is Decision.DENY
    assert not result.records[0].success
    assert result.records[0].error == "tool denied by policy"
    assert result.outputs == []


@pytest.mark.anyio
async def test_filesystem_rejects_path_escape():
    runtime = MCPAgentRuntime(
        {"filesystem": filesystem_server},
        ToolPolicy(allowed={"filesystem": {"read_text"}}),
    )
    result = await runtime.execute(
        "path escape",
        [
            PlanStep(
                server="filesystem",
                tool="read_text",
                arguments={"path": "..\\README.md"},
            )
        ],
    )
    assert result.records[0].decision is Decision.ALLOW
    assert not result.records[0].success
    assert result.outputs == []


def test_planner_is_deterministic():
    planner = RulePlanner()
    assert planner.plan("multiply 4 5") == planner.plan("multiply 4 5")
