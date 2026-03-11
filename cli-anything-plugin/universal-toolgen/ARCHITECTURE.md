# Architecture

```text
Inputs (repo, openapi, local cli)
  -> Analyzer (repo analyzer, api parser)
  -> Generator (tool schema, dynamic cli, mcp/openai exports)
  -> Runtime (python func, subprocess cli, http executor)
  -> Outputs (CLI commands, MCP tools, AI-agent tool schemas)
```

## Core modules

- `schema.py`: normalized tool schema for all targets.
- `api_parser.py`: OpenAPI/Swagger parser.
- `command_generator.py`: Typer dynamic command registration.
- `runtime_executor.py`: execution engine.
- `mcp_generator.py`: MCP/OpenAI export.
- `tool_index.py`: keyword index for token-efficient retrieval.
