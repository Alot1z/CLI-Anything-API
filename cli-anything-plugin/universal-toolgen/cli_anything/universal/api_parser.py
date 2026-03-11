"""OpenAPI parsing into ToolSchema entries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .schema import AuthConfig, ExecutionType, ParameterSchema, ToolSchema

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}


class OpenAPIParser:
    def parse_file(self, file_path: str | Path) -> list[ToolSchema]:
        raw = Path(file_path).read_text(encoding="utf-8")
        data = json.loads(raw) if str(file_path).endswith(".json") else yaml.safe_load(raw)
        return self.parse_spec(data)

    def parse_spec(self, spec: dict[str, Any]) -> list[ToolSchema]:
        tools: list[ToolSchema] = []
        servers = spec.get("servers") or []
        base_url = servers[0].get("url", "") if servers else ""
        security_schemes = spec.get("components", {}).get("securitySchemes", {})
        default_auth = self._resolve_auth(security_schemes)

        for path, operations in spec.get("paths", {}).items():
            for method, operation in operations.items():
                if method not in HTTP_METHODS:
                    continue
                op_id = operation.get("operationId") or self._operation_id(method, path)
                tags = operation.get("tags") or ["api"]
                group = tags[0].replace(" ", "-").lower()
                tool_name = f"{group}.{op_id}"
                parameters = self._parse_parameters(operation, path)
                description = operation.get("summary") or operation.get("description") or tool_name
                tools.append(
                    ToolSchema(
                        name=tool_name,
                        description=description,
                        parameters=parameters,
                        execution_type=ExecutionType.REST_API,
                        execution_target=f"{base_url}{path}" if base_url else path,
                        method=method.upper(),
                        auth=default_auth,
                        metadata={"path": path, "group": group},
                    )
                )
        return tools

    def _parse_parameters(self, operation: dict[str, Any], path: str) -> list[ParameterSchema]:
        params: list[ParameterSchema] = []
        seen: set[str] = set()
        for match in self._path_variables(path):
            seen.add(match)
            params.append(ParameterSchema(name=match, required=True, location="path", description=f"Path parameter {match}"))

        for param in operation.get("parameters", []):
            name = param.get("name")
            if not name or name in seen:
                continue
            schema = param.get("schema", {})
            params.append(
                ParameterSchema(
                    name=name,
                    param_type=schema.get("type", "string"),
                    required=param.get("required", False),
                    description=param.get("description", ""),
                    location=param.get("in", "query"),
                    default=schema.get("default"),
                )
            )
            seen.add(name)
        return params

    @staticmethod
    def _path_variables(path: str) -> list[str]:
        out = []
        for part in path.split("/"):
            if part.startswith("{") and part.endswith("}"):
                out.append(part[1:-1])
        return out

    @staticmethod
    def _operation_id(method: str, path: str) -> str:
        cleaned = path.strip("/").replace("/", "_").replace("{", "").replace("}", "") or "root"
        return f"{method}_{cleaned}"

    @staticmethod
    def _resolve_auth(security_schemes: dict[str, Any]) -> AuthConfig:
        for _, conf in security_schemes.items():
            if conf.get("type") == "http" and conf.get("scheme") == "bearer":
                return AuthConfig(kind="bearer", token_env="CLI_ANYTHING_API_TOKEN", header_name="Authorization")
            if conf.get("type") == "apiKey":
                location = conf.get("in", "header")
                key_name = conf.get("name", "X-API-Key")
                return AuthConfig(
                    kind="api_key",
                    token_env="CLI_ANYTHING_API_KEY",
                    header_name=key_name if location == "header" else "Authorization",
                    location=location,
                    query_name=key_name,
                )
        return AuthConfig()
