"""Core schema types for universal tool generation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ExecutionType(str, Enum):
    LOCAL_CLI = "local_cli"
    PYTHON_FUNCTION = "python_function"
    REST_API = "rest_api"


@dataclass(slots=True)
class ParameterSchema:
    name: str
    param_type: str = "string"
    required: bool = False
    description: str = ""
    location: str = "query"
    default: Any = None


@dataclass(slots=True)
class AuthConfig:
    kind: str = "none"
    token_env: str | None = None
    header_name: str = "Authorization"
    location: str = "header"
    query_name: str | None = None


@dataclass(slots=True)
class ToolSchema:
    name: str
    description: str
    parameters: list[ParameterSchema] = field(default_factory=list)
    execution_type: ExecutionType = ExecutionType.PYTHON_FUNCTION
    execution_target: str = ""
    method: str = "GET"
    auth: AuthConfig = field(default_factory=AuthConfig)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_openai_tool(self) -> dict[str, Any]:
        properties = {}
        required: list[str] = []
        for param in self.parameters:
            properties[param.name] = self._param_json_schema(param)
            if param.required:
                required.append(param.name)

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required,
                },
            },
        }

    @staticmethod
    def _param_json_schema(param: ParameterSchema) -> dict[str, Any]:
        param_type = param.param_type.lower()
        mapping = {
            "string": "string",
            "integer": "integer",
            "number": "number",
            "boolean": "boolean",
            "array": "array",
            "object": "object",
        }
        schema: dict[str, Any] = {
            "type": mapping.get(param_type, "string"),
            "description": param.description,
        }
        if param.default is not None:
            schema["default"] = param.default
        return schema

    def to_mcp_tool(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.to_openai_tool()["function"]["parameters"],
            "metadata": {
                "execution_type": self.execution_type.value,
                "execution_target": self.execution_target,
                "method": self.method,
                **self.metadata,
            },
        }
