import asyncio
import os
import sys
from mcp.client.stdio import stdio_client, StdioServerParameters
from mcp.client.session import ClientSession

async def main():
    print("Testing prompt-lang-generator MCP server...")

    server_script = "mcp/prompt_lang_mcp_server.py"
    env = os.environ.copy()

    server_params = StdioServerParameters(
        command="python3",
        args=[server_script],
        env=env
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                tools = await session.list_tools()
                print(f"Tools: {[t.name for t in tools.tools]}")

                # Verify generate_prompt is present
                if "generate_prompt" in [t.name for t in tools.tools]:
                    print("SUCCESS: generate_prompt tool found.")
                else:
                    print("FAILURE: generate_prompt tool not found.")
                    sys.exit(1)

                # Force call generation to test error handling
                print("Calling generate_prompt...")
                result = await session.call_tool("generate_prompt", {"requirements": "Create a skill to summarize academic papers"})
                print("Result received:")
                for content in result.content:
                    print(content.text[:200] + "...")
    except Exception as e:
        print(f"Error: {e}")
        # Print full traceback
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
