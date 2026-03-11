from __future__ import annotations

import json
from pathlib import Path

import typer

from .api_parser import OpenAPIParser
from .mcp_generator import export_mcp_manifest, export_openai_tools
from .runtime_executor import RuntimeExecutor

app = typer.Typer(help="CLI-Anything Universal Tool Generator")


@app.command("from-openapi")
def from_openapi(
    spec_path: Path = typer.Argument(..., exists=True, readable=True),
    export_mcp: Path | None = typer.Option(None, "--export-mcp"),
    export_openai: Path | None = typer.Option(None, "--export-openai"),
) -> None:
    """Parse an OpenAPI spec and export schema artifacts."""
    parser = OpenAPIParser()
    tools = parser.parse_file(spec_path)

    if export_mcp:
        export_mcp.write_text(json.dumps(export_mcp_manifest(tools), indent=2), encoding="utf-8")
    if export_openai:
        export_openai.write_text(json.dumps(export_openai_tools(tools), indent=2), encoding="utf-8")

    typer.echo(json.dumps({"tool_count": len(tools), "tools": [t.name for t in tools]}, indent=2))


@app.command("exec-openapi-tool")
def exec_openapi_tool(
    spec_path: Path = typer.Argument(..., exists=True, readable=True),
    tool_name: str = typer.Argument(..., help="Tool name from parsed OpenAPI output."),
    params: str = typer.Option("{}", "--params", help="JSON object of tool arguments."),
) -> None:
    """Execute one parsed OpenAPI tool with JSON params."""
    parser = OpenAPIParser()
    tools = {tool.name: tool for tool in parser.parse_file(spec_path)}
    if tool_name not in tools:
        raise typer.BadParameter(f"Unknown tool '{tool_name}'.")

    try:
        parsed_params = json.loads(params)
    except json.JSONDecodeError as exc:
        raise typer.BadParameter(f"Invalid JSON for --params: {exc}") from exc

    if not isinstance(parsed_params, dict):
        raise typer.BadParameter("--params must decode to a JSON object.")

    runtime = RuntimeExecutor()
    result = runtime.execute(tools[tool_name], parsed_params)
    typer.echo(json.dumps(result, indent=2, default=str))


def run() -> None:
    app()


if __name__ == "__main__":
    run()
