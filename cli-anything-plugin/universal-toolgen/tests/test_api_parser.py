from cli_anything.universal.api_parser import OpenAPIParser


def test_parse_openapi_spec_extracts_tools():
    spec = {
        "openapi": "3.0.0",
        "servers": [{"url": "https://example.com"}],
        "paths": {
            "/users/{user_id}": {
                "get": {
                    "operationId": "get_user",
                    "tags": ["users"],
                    "summary": "Get user",
                    "parameters": [
                        {"name": "expand", "in": "query", "required": False, "schema": {"type": "string"}}
                    ],
                }
            }
        },
    }

    tools = OpenAPIParser().parse_spec(spec)
    assert len(tools) == 1
    tool = tools[0]
    assert tool.name == "users.get_user"
    assert tool.execution_target == "https://example.com/users/{user_id}"
    assert {p.name for p in tool.parameters} == {"user_id", "expand"}
