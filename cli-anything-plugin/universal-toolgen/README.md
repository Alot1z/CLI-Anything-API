# CLI-Anything Universal Tool Generator

This extension adds a universal pipeline to generate and execute tools from OpenAPI specs, local commands, and python functions.

## Features

- OpenAPI parser -> unified internal `ToolSchema`
- Dynamic Typer command generation
- Unified runtime executor for local CLI / python / HTTP
- MCP tool manifest generation
- OpenAI-compatible tool schema export
- Token-efficient tool discovery index

## Quick start

```bash
cd cli-anything-plugin/universal-toolgen
pip install -e .
cli-anything-universal from-openapi examples/sample_openapi.yaml --export-mcp examples/mcp.json --export-openai examples/openai_tools.json
```
