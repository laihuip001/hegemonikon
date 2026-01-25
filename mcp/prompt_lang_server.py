#!/usr/bin/env python3
"""
Prompt-Lang Generator MCP Server
================================

Exposes Prompt-Lang tools via MCP.
"""

import sys
import os
import io
import json
from pathlib import Path

# ============ Platform-specific asyncio setup ============
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ============ Redirect stdout to stderr ============
# This prevents any accidental stdout pollution from imported modules
_original_stdout = sys.stdout
_stderr_wrapper = sys.stderr

def log(msg):
    print(f"[prompt-lang-mcp] {msg}", file=sys.stderr, flush=True)

# ============ Import path setup ============
# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "forge" / "prompt-lang"))

# Import MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError as e:
    log(f"MCP import error: {e}")
    sys.exit(1)

# Import Prompt-Lang
try:
    from prompt_lang import PromptLangParser, ParseError
    log("Prompt-Lang imported successfully")
except ImportError as e:
    log(f"Prompt-Lang import error: {e}")
    sys.exit(1)

server = Server(
    name="prompt-lang-generator",
    version="1.0.0",
    instructions="Generate, parse, and validate Prompt-Lang v2 code."
)

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="generate",
            description="Generate a Prompt-Lang definition from natural language requirements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "Natural language description of the desired prompt/skill."
                    }
                },
                "required": ["requirements"]
            }
        ),
        Tool(
            name="parse",
            description="Parse Prompt-Lang code into JSON AST.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Prompt-Lang code content."
                    }
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="validate",
            description="Validate Prompt-Lang code syntax.",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {
                        "type": "string",
                        "description": "Prompt-Lang code content."
                    }
                },
                "required": ["code"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    log(f"call_tool: {name}")

    if name == "generate":
        req = arguments.get("requirements", "")
        if not req:
            return [TextContent(type="text", text="Error: requirements is required")]

        # Load template
        template_path = REPO_ROOT / ".agent/skills/utils/prompt-lang-generator/templates/base_template.yaml"
        if not template_path.exists():
             # Fallback to empty template if file missing
             log(f"Template not found at {template_path}")
             template = "#prompt {name}\n\n@role:\n  ...\n\n@goal:\n  ...\n"
        else:
             template = template_path.read_text(encoding="utf-8")

        # Simple filling (Placeholder logic as full LLM generation is not available)
        output = f"""// Generated from requirements: {req}
// Note: This is a scaffold. Fill in specific logic.

{template}
"""
        return [TextContent(type="text", text=output)]

    elif name == "parse":
        code = arguments.get("code", "")
        if not code:
            return [TextContent(type="text", text="Error: code is required")]

        try:
            parser = PromptLangParser(code)
            prompt = parser.parse()
            if prompt:
                return [TextContent(type="text", text=prompt.to_json())]
            else:
                return [TextContent(type="text", text="Error: Parsing failed (None returned)")]
        except Exception as e:
            return [TextContent(type="text", text=f"Parse Error: {e}")]

    elif name == "validate":
        code = arguments.get("code", "")
        if not code:
             return [TextContent(type="text", text="Error: code is required")]

        try:
            parser = PromptLangParser(code)
            prompt = parser.parse()

            errors = []
            if not prompt:
                return [TextContent(type="text", text="Invalid: Parsing returned None")]

            if not prompt.role:
                errors.append("Missing required block: @role")
            if not prompt.goal:
                errors.append("Missing required block: @goal")

            if errors:
                return [TextContent(type="text", text=f"Invalid:\n" + "\n".join(errors))]
            else:
                return [TextContent(type="text", text="Valid")]
        except Exception as e:
            return [TextContent(type="text", text=f"Invalid (Parse Error): {e}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    async with stdio_server() as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options()
        )

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        log(f"Fatal error: {e}")
        sys.exit(1)
