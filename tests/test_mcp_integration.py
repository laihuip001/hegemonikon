
import asyncio
import os
import sys
from pathlib import Path
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def main():
    print("Testing prompt-lang-generator MCP server...")

    script_path = Path("mcp/prompt_lang_mcp_server.py")
    if not script_path.exists():
        print(f"Error: {script_path} not found")
        sys.exit(1)

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(script_path)],
        env=os.environ.copy()
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # List tools
                tools = await session.list_tools()
                print(f"Tools found: {[t.name for t in tools.tools]}")

                if "generate" not in [t.name for t in tools.tools]:
                    print("Error: 'generate' tool not found")
                    sys.exit(1)

                # Call tool
                print("Calling 'generate' tool...")
                result = await session.call_tool("generate", arguments={
                    "requirements": "Create a python script to calculate fibonacci numbers",
                    "domain": "coding"
                })

                content = result.content[0].text
                print("\n--- Generated Output Start ---")
                print(content[:200] + "...")
                print("--- Generated Output End ---\n")

                if "AI Assistant specialized in: Create a python script" in content:
                    print("SUCCESS: Output contains expected content.")
                else:
                    print("FAILURE: Output missing expected content.")
                    sys.exit(1)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
