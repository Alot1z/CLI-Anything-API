from cli_anything.universal.mcp_generator import export_mcp_manifest
from cli_anything.universal.schema import ToolSchema


def test_export_mcp_manifest_contains_tools():
    tools = [ToolSchema(name="users.list", description="List users")]
    manifest = export_mcp_manifest(tools)
    assert manifest["name"] == "cli-anything-universal"
    assert manifest["tools"][0]["name"] == "users.list"
