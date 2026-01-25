#!/usr/bin/env python3
"""
Prompt-Lang Generator MCP Server
================================

Exposes Prompt-Lang generation as an MCP tool.
"""

import sys
import os
import json
import logging
import asyncio
from pathlib import Path
from datetime import datetime

# ============ CRITICAL: Platform-specific asyncio setup ============
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ============ CRITICAL: Redirect ALL stdout to stderr ============
import io
_original_stdout = sys.stdout

def log(msg):
    print(f"[prompt-lang-mcp] {msg}", file=sys.stderr, flush=True)

# Import MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    import google.generativeai as genai
except ImportError as e:
    log(f"Import error: {e}")
    sys.exit(1)

# Initialize Server
server = Server(
    name="prompt-lang-generator",
    version="1.0.0",
    instructions="Generates Prompt-Lang code from natural language requirements."
)

# Setup paths based on script location
REPO_ROOT = Path(__file__).parent.parent
LOG_DIR = REPO_ROOT / "forge/prompt-lang/logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "execution.jsonl"
TEMPLATE_DIR = REPO_ROOT / "forge/prompt-lang/templates"

def log_execution(requirements, prompt_code, model_name="gemini-1.5-flash"):
    """Log execution for meta-learning loop."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "requirements": requirements,
        "output": prompt_code,
        "model": model_name
    }
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as e:
        log(f"Failed to write log: {e}")

# Load Templates
try:
    BASE_TEMPLATE = (TEMPLATE_DIR / "base_template.yaml").read_text(encoding="utf-8")
except Exception as e:
    BASE_TEMPLATE = "role: {{role}}\ngoal: {{goal}}"
    log(f"Warning: base_template.yaml not found at {TEMPLATE_DIR}, using fallback. Error: {e}")

# Configure Gemini
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    log("Warning: GEMINI_API_KEY not set.")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="generate_prompt",
            description="Generate a structured Prompt-Lang definition from natural language requirements.",
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
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name != "generate_prompt":
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    requirements = arguments.get("requirements")
    if not requirements:
        return [TextContent(type="text", text="Error: requirements are required")]

    log(f"Generating prompt for: {requirements[:50]}...")

    if not API_KEY:
        return [TextContent(type="text", text="Error: GEMINI_API_KEY not set.")]

    try:
        # Construct System Prompt
        system_prompt = f"""
You are the Prompt-Lang Generator. Your task is to convert natural language requirements into a valid Prompt-Lang v2.0 definition.

Reference Template:
```yaml
{BASE_TEMPLATE}
```

Rules:
1. Output MUST be valid Prompt-Lang code (starting with #prompt <name>).
2. Include @role, @goal, @constraints, @format, @examples.
3. Use the reference template structure.
4. Do not include markdown code fences (```) around the whole output, just the raw content, unless it is part of the file format (Prompt-Lang does not require outer fences, but @format block does).
5. Actually, outputting markdown code block ```prompt-lang ... ``` is acceptable for display, but the raw content is preferred. Let's output raw text.

Requirements:
{requirements}
"""
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(system_prompt)
        generated_code = response.text

        # Log for meta-learning
        log_execution(requirements, generated_code)

        return [TextContent(type="text", text=generated_code)]

    except Exception as e:
        log(f"Generation error: {e}")
        return [TextContent(type="text", text=f"Error generating prompt: {e}")]

async def main():
    async with stdio_server() as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
