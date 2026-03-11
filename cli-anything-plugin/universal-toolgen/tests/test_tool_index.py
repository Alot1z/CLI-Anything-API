from cli_anything.universal.schema import ToolSchema
from cli_anything.universal.tool_index import ToolIndex


def test_tool_index_search_returns_relevant_tools():
    tools = [
        ToolSchema(name="users.list", description="List users"),
        ToolSchema(name="users.create", description="Create new user"),
        ToolSchema(name="invoices.list", description="List invoices"),
    ]
    idx = ToolIndex(tools)

    result = idx.search("create user", limit=1)
    assert result[0].name == "users.create"
