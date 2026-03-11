import io
import socket
import urllib.error

from cli_anything.universal.runtime_executor import RuntimeExecutor
from cli_anything.universal.schema import AuthConfig, ExecutionType, ParameterSchema, ToolSchema


def test_execute_python_function():
    ex = RuntimeExecutor()

    def add(a: int, b: int) -> int:
        return a + b

    ex.register_function("calc.add", add)
    tool = ToolSchema(
        name="calc.add",
        description="Add numbers",
        execution_type=ExecutionType.PYTHON_FUNCTION,
        execution_target="calc.add",
    )

    result = ex.execute(tool, {"a": 2, "b": 3})
    assert result["result"] == 5


def test_execute_http_returns_structured_error_on_url_failure(monkeypatch):
    ex = RuntimeExecutor()
    tool = ToolSchema(
        name="users.list",
        description="List users",
        execution_type=ExecutionType.REST_API,
        execution_target="https://invalid.example/users",
    )

    def raise_url_error(*_args, **_kwargs):
        raise urllib.error.URLError("dns failure")

    monkeypatch.setattr("urllib.request.urlopen", raise_url_error)
    result = ex.execute(tool, {})
    assert result["ok"] is False
    assert result["status"] is None
    assert "dns failure" in result["error"]


def test_execute_http_apikey_query_auth(monkeypatch):
    ex = RuntimeExecutor()
    tool = ToolSchema(
        name="users.list",
        description="List users",
        execution_type=ExecutionType.REST_API,
        execution_target="https://example.com/users",
        parameters=[ParameterSchema(name="limit", location="query")],
        auth=AuthConfig(kind="api_key", token_env="CLI_ANYTHING_API_KEY", location="query", query_name="api_token"),
    )

    captured = {}

    class FakeResponse:
        status = 200

        def read(self):
            return b'{"ok": true}'

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def fake_urlopen(request, timeout=30):
        captured["url"] = request.full_url
        return FakeResponse()

    monkeypatch.setenv("CLI_ANYTHING_API_KEY", "sekret")
    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    result = ex.execute(tool, {"limit": 5})
    assert result["ok"] is True
    assert "api_token=sekret" in captured["url"]


def test_execute_http_returns_http_error_payload(monkeypatch):
    ex = RuntimeExecutor()
    tool = ToolSchema(
        name="users.list",
        description="List users",
        execution_type=ExecutionType.REST_API,
        execution_target="https://example.com/users",
    )

    def raise_http_error(req, timeout=30):
        raise urllib.error.HTTPError(req.full_url, 404, "Not Found", hdrs=None, fp=io.BytesIO(b'{"error":"missing"}'))

    monkeypatch.setattr("urllib.request.urlopen", raise_http_error)
    result = ex.execute(tool, {})
    assert result["ok"] is False
    assert result["status"] == 404
    assert result["data"]["error"] == "missing"


def test_execute_http_timeout_error(monkeypatch):
    ex = RuntimeExecutor()
    tool = ToolSchema(
        name="users.list",
        description="List users",
        execution_type=ExecutionType.REST_API,
        execution_target="https://example.com/users",
    )

    def raise_timeout(*_args, **_kwargs):
        raise socket.timeout("timed out")

    monkeypatch.setattr("urllib.request.urlopen", raise_timeout)
    result = ex.execute(tool, {})
    assert result["ok"] is False
    assert result["error"] == "timeout"
