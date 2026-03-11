from cli_anything.universal.schema import ParameterSchema, ToolSchema


def test_openai_tool_keeps_parameter_types_and_defaults():
    tool = ToolSchema(
        name="users.search",
        description="Search users",
        parameters=[
            ParameterSchema(name="active", param_type="boolean", required=True),
            ParameterSchema(name="limit", param_type="integer", default=10),
            ParameterSchema(name="tags", param_type="array"),
        ],
    )

    payload = tool.to_openai_tool()
    props = payload["function"]["parameters"]["properties"]

    assert props["active"]["type"] == "boolean"
    assert props["limit"]["type"] == "integer"
    assert props["limit"]["default"] == 10
    assert props["tags"]["type"] == "array"
