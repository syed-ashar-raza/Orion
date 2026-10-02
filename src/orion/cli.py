from __future__ import annotations

import argparse
import asyncio
import json

from .agent import Agent
from .planner import RulePlanner
from .policy import ToolPolicy
from .runtime import MCPAgentRuntime
from .servers.calculator import mcp as calculator_server
from .servers.filesystem import mcp as filesystem_server

SERVERS = {
    "calculator": calculator_server,
    "filesystem": filesystem_server,
}


def _runtime() -> MCPAgentRuntime:
    return MCPAgentRuntime(
        SERVERS,
        ToolPolicy(
            allowed={
                "calculator": {"add", "multiply"},
                "filesystem": {"list_files", "read_text"},
            }
        ),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Orion MCP-native agent orchestration platform"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("discover", help="Discover MCP tools")

    run = sub.add_parser("run", help="Run a deterministic agent task")
    run.add_argument("task")

    serve = sub.add_parser("serve", help="Serve an MCP server over Streamable HTTP")
    serve.add_argument("server", choices=SERVERS, help="MCP server to expose")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    serve.add_argument("--path", default="/mcp")

    args = parser.parse_args()

    if args.command == "serve":
        try:
            asyncio.run(
                SERVERS[args.server].run_streamable_http_async(
                    host=args.host,
                    port=args.port,
                    streamable_http_path=args.path,
                )
            )
        except KeyboardInterrupt:
            return
        return

    runtime = _runtime()

    if args.command == "discover":
        print(
            json.dumps(
                [tool.model_dump(mode="json") for tool in asyncio.run(runtime.discover_tools())],
                indent=2,
            )
        )
        return

    result = asyncio.run(Agent(RulePlanner(), runtime).run(args.task))
    print(json.dumps(result.model_dump(mode="json"), indent=2))

