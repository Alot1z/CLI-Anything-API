"""Unified runtime executor for CLI, python callables, and HTTP."""

from __future__ import annotations

import json
import os
import shlex
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from http import HTTPStatus
from typing import Any

from .schema import ExecutionType, ToolSchema


class RuntimeExecutor:
    def __init__(self) -> None:
        self._functions: dict[str, Callable[..., Any]] = {}

    def register_function(self, target: str, func: Callable[..., Any]) -> None:
        self._functions[target] = func

    def execute(self, tool: ToolSchema, args: dict[str, Any]) -> dict[str, Any]:
        if tool.execution_type == ExecutionType.PYTHON_FUNCTION:
            return self._execute_python(tool, args)
        if tool.execution_type == ExecutionType.LOCAL_CLI:
            return self._execute_cli(tool, args)
        if tool.execution_type == ExecutionType.REST_API:
            return self._execute_http(tool, args)
        raise ValueError(f"Unsupported execution type: {tool.execution_type}")

    def _execute_python(self, tool: ToolSchema, args: dict[str, Any]) -> dict[str, Any]:
        func = self._functions.get(tool.execution_target)
        if not func:
            raise KeyError(f"No function registered for {tool.execution_target}")
        return {"result": func(**args)}

    def _execute_cli(self, tool: ToolSchema, args: dict[str, Any]) -> dict[str, Any]:
        cmd = [*shlex.split(tool.execution_target)]
        for key, val in args.items():
            flag = f"--{key.replace('_', '-')}"
            if isinstance(val, bool):
                if val:
                    cmd.append(flag)
            else:
                cmd.extend([flag, str(val)])

        proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
        return {
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }

    def _execute_http(self, tool: ToolSchema, args: dict[str, Any]) -> dict[str, Any]:
        path_args = {p.name: args[p.name] for p in tool.parameters if p.location == "path" and p.name in args}
        query_args = {p.name: args[p.name] for p in tool.parameters if p.location == "query" and p.name in args}

        url = tool.execution_target
        for key, value in path_args.items():
            url = url.replace(f"{{{key}}}", urllib.parse.quote(str(value)))

        headers = {"Content-Type": "application/json"}
        if tool.auth.token_env and os.getenv(tool.auth.token_env):
            token = os.getenv(tool.auth.token_env)
            if tool.auth.kind == "bearer":
                headers[tool.auth.header_name] = f"Bearer {token}"
            elif tool.auth.kind == "api_key":
                if tool.auth.location == "query" and tool.auth.query_name:
                    query_args[tool.auth.query_name] = token
                elif tool.auth.location == "header":
                    headers[tool.auth.header_name] = token
                elif tool.auth.location == "cookie" and tool.auth.query_name:
                    headers["Cookie"] = f"{tool.auth.query_name}={token}"

        if query_args:
            encoded = urllib.parse.urlencode(query_args)
            sep = "&" if "?" in url else "?"
            url = f"{url}{sep}{encoded}"

        req = urllib.request.Request(url=url, method=tool.method, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                payload = response.read().decode("utf-8")
                return {"status": response.status, "ok": True, "data": self._parse_payload(payload)}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8") if exc.fp else ""
            return {
                "status": exc.code,
                "ok": False,
                "error": HTTPStatus(exc.code).phrase if exc.code in HTTPStatus._value2member_map_ else "HTTP Error",
                "data": self._parse_payload(body),
            }
        except urllib.error.URLError as exc:
            return {"status": None, "ok": False, "error": str(exc.reason), "data": None}
        except TimeoutError:
            return {"status": None, "ok": False, "error": "timeout", "data": None}

    @staticmethod
    def _parse_payload(payload: str) -> Any:
        try:
            return json.loads(payload)
        except json.JSONDecodeError:
            return payload
