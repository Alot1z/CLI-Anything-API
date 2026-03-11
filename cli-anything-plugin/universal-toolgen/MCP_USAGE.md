# MCP Usage

Generate an MCP manifest from an OpenAPI spec:

```bash
cli-anything-universal from-openapi examples/sample_openapi.yaml --export-mcp examples/mcp.json
```

The generated `mcp.json` contains `tools[]` objects with `inputSchema` and execution metadata used by an MCP server adapter.
