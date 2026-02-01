# PROOF: [L3/テスト] <- mekhane/symploke/tests/ 対象モジュールが存在→検証が必要→test_mcp_integration が担う
#!/usr/bin/env python3
"""
MCP Server Integration Test

Tests the Jules MCP Server by simulating tool calls.
"""

import asyncio
import os
import sys
import json
import pytest

sys.path.insert(0, "/home/laihuip001/oikos/hegemonikon")


@pytest.mark.asyncio
@pytest.mark.skipif(not os.environ.get("JULES_API_KEY"), reason="JULES_API_KEY not set")
async def test_mcp_tools():
    """Test MCP server tools directly."""
    print("=" * 70)
    print("Jules MCP Server - Integration Test")
    print("=" * 70)

    # Import the server module (local, not from mcp package)
    sys.path.insert(0, "/home/laihuip001/oikos/hegemonikon/mcp")
    import jules_mcp_server as server

    print("\n[1] Testing list_tools...")
    tools = await server.list_tools()
    print(f"  Found {len(tools)} tools:")
    for tool in tools:
        print(f"    - {tool.name}: {tool.description[:50]}...")

    print("\n[2] Testing jules_list_repos...")
    result = await server.call_tool("jules_list_repos", {})
    print(f"  Result: {result[0].text[:100]}...")

    print("\n[3] Testing jules_get_status with existing session...")
    # Use a session ID from earlier tests
    result = await server.call_tool(
        "jules_get_status", {"session_id": "10287138985978924050"}
    )
    print(f"  Result:\n{result[0].text}")

    print("\n[4] Testing jules_create_task...")
    result = await server.call_tool(
        "jules_create_task",
        {
            "prompt": "Add MCP integration test comment to README.md",
            "repo": "laihuip001/dev-rules",
            "branch": "main",
        },
    )
    print(f"  Result:\n{result[0].text}")

    print("\n" + "=" * 70)
    print("All MCP tools tested successfully!")
    return True


if __name__ == "__main__":
    # Set API key
    api_key = os.environ.get("JULES_API_KEY")
    if not api_key:
        print("❌ JULES_API_KEY not set")
        sys.exit(1)

    print(f"API Key: {api_key[:10]}...{api_key[-4:]}")

    try:
        result = asyncio.run(test_mcp_tools())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
