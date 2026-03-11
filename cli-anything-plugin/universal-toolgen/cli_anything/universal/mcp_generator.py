"""MCP and agent-tool export helpers."""

from __future__ import annotations

from typing import Any

from .schema import ToolSchema


def export_mcp_manifest(tools: list[ToolSchema]) -> dict[str, Any]:
    return {
        "name": "cli-anything-universal",
        "version": "0.1.0",
        "tools": [tool.to_mcp_tool() for tool in tools],
    }


def export_openai_tools(tools: list[ToolSchema]) -> list[dict[str, Any]]:
    return [tool.to_openai_tool() for tool in tools]
