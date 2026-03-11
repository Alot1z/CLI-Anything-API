# Research Notes

## Existing repository observations

- Current repository is organized as multiple generated agent harnesses (`<software>/agent-harness`).
- Harnesses use Python + Click and expose software-specific command groups.
- No single shared API/OpenAPI ingestion module exists in the root.

## Integration risks

- Command name collisions across tools generated from different APIs.
- Inconsistent auth handling across OpenAPI specs.
- Dynamic CLI option generation can create unstable UX for agents.

## Design choices

- Use a stable internal schema (`ToolSchema`) as the single source of truth.
- Keep execution unified under one runtime executor abstraction.
- Export to MCP/OpenAI schemas from the same model to avoid drift.
