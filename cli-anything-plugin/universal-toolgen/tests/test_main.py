import json

import pytest
import typer

from cli_anything.universal.main import exec_openapi_tool


def _write_spec(path):
    path.write_text(
        json.dumps(
            {
                "openapi": "3.0.0",
                "paths": {"/ping": {"get": {"operationId": "ping", "tags": ["api"]}}},
            }
        ),
        encoding="utf-8",
    )


def test_exec_openapi_tool_rejects_invalid_json(tmp_path):
    spec = tmp_path / "spec.json"
    _write_spec(spec)

    with pytest.raises(typer.BadParameter):
        exec_openapi_tool(spec, "api.ping", params="{not json}")


def test_exec_openapi_tool_rejects_non_object_params(tmp_path):
    spec = tmp_path / "spec.json"
    _write_spec(spec)

    with pytest.raises(typer.BadParameter):
        exec_openapi_tool(spec, "api.ping", params='[1,2,3]')
