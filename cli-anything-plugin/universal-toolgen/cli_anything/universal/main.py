from __future__ import annotations

import json
from pathlib import Path

import typer

from .api_parser import OpenAPIParser
from .command_generator import DynamicCLI
from .mcp_generator import export_mcp_manifest, export_openai_tools
from .runtime_executor import RuntimeExecutor

app = typer.Typer(help="CLI-Anything Universal Tool Generator")


@app.command("from-openapi")
def from_openapi(
    spec_path: Path = typer.Argument(..., exists=True, readable=True),
    export_mcp: Path | None = typer.Option(None, "--export-mcp"),
    export_openai: Path | None = typer.Option(None, "--export-openai"),
) -> None:
    parser = OpenAPIParser()
    tools = parser.parse_file(spec_path)

    if export_mcp:
        export_mcp.write_text(json.dumps(export_mcp_manifest(tools), indent=2), encoding="utf-8")
    if export_openai:
        export_openai.write_text(json.dumps(export_openai_tools(tools), indent=2), encoding="utf-8")

    runtime = RuntimeExecutor()
    dyn = DynamicCLI(tools, runtime)
    cli = dyn.build()
    cli()


def run() -> None:
    app()


if __name__ == "__main__":
    run()
