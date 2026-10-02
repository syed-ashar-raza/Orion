# Orion

### MCP + Modern Agent Architecture

Production-oriented, MCP-native agent orchestration with explicit tool discovery, planning, policy enforcement, execution, and structured traces.

## What Orion proves

Orion is the portfolio project for the **MCP + modern agent architecture** capability. It is deliberately different from AgentForge: AgentForge demonstrates basic tool-using agents, while Orion demonstrates a protocol-native architecture around MCP servers, discovery, authorization, planning, and execution.

The local planner is deterministic so the core architecture can be tested reproducibly. The `Planner` interface is replaceable with an LLM-backed planner without changing the runtime or policy boundary.

## Architecture

```text
                         ORION
              MCP-Native Agent Runtime
                         |
                +--------+--------+
                |                 |
             Planner          MCP Client
                |                 |
             PlanStep       Tool Discovery
                |                 |
                +--------+--------+
                         |
                  Policy Engine
                         |
                  ALLOW / DENY
                         |
                    MCP Tool Call
                         |
             +-----------+-----------+
             |                       |
       Calculator MCP        Filesystem MCP
             |                       |
             +-----------+-----------+
                         |
                  Structured Result
                         |
                   Execution Trace
```

## Capabilities

- MCP server construction with `FastMCP`
- MCP client connections
- In-process MCP testing
- Tool discovery with `list_tools`
- Tool execution with `call_tool`
- Typed tool schemas
- Explicit tool authorization
- Default-deny behavior for unspecified tools
- Planner/runtime separation
- Multi-server runtime design
- Structured execution records
- Streamable HTTP-ready MCP servers

The official MCP Python SDK currently documents v2 as its stable line and supports Python 3.10+, MCP clients/servers, stdio, Streamable HTTP, and SSE transports. 

## Components

```text
src/orion/
├── agent.py
├── cli.py
├── models.py
├── planner.py
├── policy.py
├── runtime.py
└── servers/
    ├── calculator.py
    └── filesystem.py
```

## Quick start

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Validate:

```powershell
python -m pytest
python -m ruff check .
```

Discover MCP tools:

```powershell
orion discover
```

Run the deterministic agent:

```powershell
orion run "add 2 3"
orion run "multiply 4 5"
```

Expected output for `add 2 3` includes a successful authorized execution and result `5.0`.

## MCP transport

Each server can run directly using the SDK's default stdio execution model:

```powershell
python -m orion.servers.calculator
```

For deployable HTTP transport, the SDK supports Streamable HTTP:

```python
mcp.run(transport="streamable-http")
```

The standard MCP endpoint is `/mcp` when using the default Streamable HTTP setup.

## Authorization boundary

Orion does not implicitly trust discovered tools.

```text
discover tool
     |
     v
policy lookup
     |
  +--+--+
  |     |
ALLOW  DENY
  |     |
  v     v
execute stop
```

An empty or missing allowlist does not grant access. Argument-size limits are also enforced before execution.

This is an agent-architecture authorization boundary, not a replacement for Sentinel. Sentinel remains the dedicated AI-security project.

## Testing strategy

Tests use the SDK's in-process `Client(mcp)` capability, avoiding subprocesses and network ports while exercising the MCP client/server boundary.

Coverage includes:

- MCP tool discovery
- MCP tool invocation
- Structured results
- Agent execution
- Authorization denial
- Deterministic planning

## Scope and limitations

Orion v1.0.0 is an architecture-focused portfolio implementation.

It is **not**:

- a general autonomous agent
- an LLM benchmark
- a replacement for an MCP host
- a universal tool-security solution
- a production identity/authentication system
- proof of internet-scale performance

The deterministic planner exists to make behavior reproducible. The `Planner` interface is the extension point for a model-backed planner.

## Design principles

1. **Protocol-native** — use MCP rather than inventing a private tool protocol.
2. **Explicit authorization** — discovered does not mean trusted.
3. **Planner/runtime separation** — planning is replaceable; execution controls remain stable.
4. **Structured execution** — tool results and execution records are machine-readable.
5. **Deterministic evidence** — core tests are repeatable locally.
6. **Small surface area** — no feature is added without architectural value.

## Version

`1.0.0`

## License

Apache-2.0
