from pathlib import Path

from mcp.server.mcpserver import MCPServer

ROOT = Path(__file__).resolve().parents[3] / "workspace"
ROOT.mkdir(parents=True, exist_ok=True)

mcp = MCPServer(
    "orion-filesystem",
    instructions="Read-only workspace filesystem tools.",
)


def _safe_path(relative_path: str) -> Path:
    candidate = (ROOT / relative_path).resolve()
    if candidate != ROOT and ROOT not in candidate.parents:
        raise ValueError("path escapes the Orion workspace")
    return candidate


@mcp.tool()
def list_files() -> list[str]:
    """List files in the Orion workspace."""
    return sorted(
        str(path.relative_to(ROOT))
        for path in ROOT.rglob("*")
        if path.is_file()
    )


@mcp.tool()
def read_text(path: str) -> str:
    """Read UTF-8 text from a file inside the Orion workspace."""
    target = _safe_path(path)
    if not target.is_file():
        raise ValueError("file not found")
    return target.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
