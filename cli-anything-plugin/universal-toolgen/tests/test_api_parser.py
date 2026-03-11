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


def test_parse_openapi_without_servers_uses_relative_path():
    spec = {
        "openapi": "3.0.0",
        "paths": {"/health": {"get": {"summary": "health"}}},
    }
    tools = OpenAPIParser().parse_spec(spec)
    assert tools[0].execution_target == "/health"


def test_apikey_query_auth_keeps_location():
    spec = {
        "openapi": "3.0.0",
        "components": {
            "securitySchemes": {
                "apiKeyAuth": {"type": "apiKey", "name": "api_token", "in": "query"}
            }
        },
        "paths": {"/users": {"get": {"summary": "list users"}}},
    }
    tools = OpenAPIParser().parse_spec(spec)
    assert tools[0].auth.kind == "api_key"
    assert tools[0].auth.location == "query"
    assert tools[0].auth.query_name == "api_token"
