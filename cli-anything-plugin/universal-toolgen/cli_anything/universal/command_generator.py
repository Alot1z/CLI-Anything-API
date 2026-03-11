"""Dynamic Typer CLI generation from ToolSchema."""

from __future__ import annotations

import json
from collections import defaultdict
import typer

from .runtime_executor import RuntimeExecutor
from .schema import ToolSchema


class DynamicCLI:
    def __init__(self, tools: list[ToolSchema], executor: RuntimeExecutor) -> None:
        self.tools = tools
        self.executor = executor

    def build(self) -> typer.Typer:
        app = typer.Typer(help="CLI-Anything universal runtime")
        grouped: dict[str, list[ToolSchema]] = defaultdict(list)

        for tool in self.tools:
            group = tool.metadata.get("group", "tools")
            grouped[group].append(tool)

        for group, group_tools in grouped.items():
            sub = typer.Typer(help=f"Commands for {group}")
            for tool in group_tools:
                command_name = tool.name.split(".")[-1].replace("_", "-")
                sub.command(name=command_name)(self._make_command(tool))
            app.add_typer(sub, name=group)
        return app

    def _make_command(self, tool: ToolSchema):
        def command(params: str = typer.Option("{}", "--params", help="JSON object of tool parameters")) -> None:
            kwargs = json.loads(params)
            result = self.executor.execute(tool, kwargs)
            typer.echo(json.dumps(result, indent=2, default=str))

        command.__name__ = tool.name.replace(".", "_")
        command.__doc__ = tool.description
        return command
