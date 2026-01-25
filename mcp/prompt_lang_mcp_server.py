#!/usr/bin/env python3
"""
Prompt-Lang Generator MCP Server
================================

Exposes prompt-lang-generator as an MCP tool.
Generates Prompt-Lang code from natural language requirements.
"""

import sys
import os
import json
import time
from pathlib import Path

# ============ CRITICAL: Platform-specific asyncio setup ============
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ============ CRITICAL: Redirect ALL stdout to stderr ============
import io
_original_stdout = sys.stdout
_stderr_wrapper = sys.stderr

def log(msg):
    print(f"[prompt-lang-mcp] {msg}", file=sys.stderr, flush=True)

log("Starting Prompt-Lang MCP Server...")

# Import MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    log("MCP imports successful")
except Exception as e:
    log(f"MCP import error: {e}")
    sys.exit(1)

# Initialize MCP server
server = Server(
    name="prompt-lang-generator",
    version="1.0.0",
    instructions="Generates Prompt-Lang code from natural language requirements"
)

# Constants
BASE_TEMPLATE_PATH = Path(".agent/skills/utils/prompt-lang-generator/templates/base_template.yaml")
LOG_FILE_PATH = Path("logs/prompt_lang_gen.jsonl")

@server.list_tools()
async def list_tools():
    """List available tools."""
    return [
        Tool(
            name="generate",
            description="Generate Prompt-Lang code from natural language requirements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "Natural language description of the prompt requirements."
                    },
                    "domain": {
                        "type": "string",
                        "description": "Domain hint (e.g., technical, medical, summarization).",
                        "default": "general"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Desired output format.",
                        "default": "skill.md"
                    }
                },
                "required": ["requirements"]
            }
        )
    ]

def load_template():
    """Load the base template."""
    try:
        if BASE_TEMPLATE_PATH.exists():
            return BASE_TEMPLATE_PATH.read_text(encoding='utf-8')
        return "# Error: Base template not found"
    except Exception as e:
        log(f"Error loading template: {e}")
        return f"# Error loading template: {e}"

def log_execution(requirements: str, output: str, domain: str):
    """Log execution for meta-learning."""
    try:
        LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": time.time(),
            "requirements": requirements,
            "domain": domain,
            "output_length": len(output)
        }
        with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        log(f"Logging error: {e}")

@server.call_tool(validate_input=True)
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    log(f"call_tool: {name}")

    if name == "generate":
        reqs = arguments.get("requirements", "")
        domain = arguments.get("domain", "general")

        if not reqs:
            return [TextContent(type="text", text="Error: requirements are required")]

        log(f"Generating for requirements: {reqs[:50]}...")

        # Load template
        template = load_template()

        # Mock Generation Logic (Simulating LLM)
        # In a real implementation, this would call an LLM with the template and requirements.

        generated_code = template

        # 1. Fill Metadata
        generated_code = generated_code.replace('name: ""', f'name: "generated_skill_{int(time.time())}"')
        generated_code = generated_code.replace('owner: ""', 'owner: "Prompt-Lang Generator"')
        generated_code = generated_code.replace('last_updated: ""', f'last_updated: "{time.strftime("%Y-%m-%d")}"')

        # 2. Fill Required Directives
        generated_code = generated_code.replace(
            '# AI の役割を1-2文で定義\n    # 例: シニアコードレビューア（セキュリティ専門）',
            f'AI Assistant specialized in: {reqs}'
        )

        generated_code = generated_code.replace(
            '# タスクの目的を明確に記述\n    # 例: 提示されたコードの品質とセキュリティを評価し、改善提案を出す',
            f'To satisfy the following requirements: {reqs}'
        )

        generated_code = generated_code.replace(
            '- ""  # 制約1',
            '- "Must adhere strictly to the user requirements"'
        )
        generated_code = generated_code.replace(
            '- ""  # 制約2',
            f'- "Focus on the domain: {domain}"'
        )
        generated_code = generated_code.replace(
            '- ""  # 制約3',
            '- "Ensure output is concise and helpful"'
        )

        # 3. Fill Examples
        generated_code = generated_code.replace(
            '- input: ""\n      output: ""',
            '- input: "Sample Input"\n      output: "Sample Output based on requirements"'
        )

        # Log execution
        log_execution(reqs, generated_code, domain)

        return [TextContent(type="text", text=generated_code)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    """Run the MCP server."""
    log("Starting stdio server...")
    try:
        async with stdio_server() as streams:
            log("stdio_server connected")
            await server.run(
                streams[0],  # read_stream
                streams[1],  # write_stream
                server.create_initialization_options()
            )
    except Exception as e:
        log(f"Server error: {e}")
        raise

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Server stopped by user")
    except Exception as e:
        log(f"Fatal error: {e}")
        sys.exit(1)
