#!/usr/bin/env python3
"""
Prompt-Lang Generator MCP Server
================================

MCP server that generates Prompt-Lang code from natural language requirements.
Implements Phase C of the Prompt-Lang integration.

- Tool: generate_prompt
- Backend: Google Gemini
- Logging: forge/prompt-lang/logs/execution.jsonl (for Meta-learning)
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime
import io

# ============ CRITICAL: Platform-specific asyncio setup ============
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ============ CRITICAL: Redirect ALL stdout to stderr ============
_original_stdout = sys.stdout
_stderr_wrapper = sys.stderr

def log(msg):
    print(f"[prompt-lang-mcp] {msg}", file=sys.stderr, flush=True)

# Suppress stdout during imports
class StdoutSuppressor:
    def __init__(self):
        self._null = io.StringIO()
        self._old_stdout = None

    def __enter__(self):
        self._old_stdout = sys.stdout
        sys.stdout = self._null
        return self

    def __exit__(self, *args):
        sys.stdout = self._old_stdout

log("Starting Prompt-Lang MCP Server...")

# Import dependencies
try:
    with StdoutSuppressor():
        import google.generativeai as genai
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
    log("Imports successful")
except Exception as e:
    log(f"Import error: {e}")
    sys.exit(1)

# Setup Logging
LOG_DIR = Path("forge/prompt-lang/logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
EXECUTION_LOG = LOG_DIR / "execution.jsonl"

def log_execution(input_req, output_code):
    try:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "input": input_req,
            "output": output_code
        }
        with open(EXECUTION_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        log("Execution logged")
    except Exception as e:
        log(f"Logging error: {e}")

# Setup Gemini
API_KEY = os.getenv("GEMINI_API_KEY")
model = None
if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        log("Gemini configured")
    except Exception as e:
        log(f"Gemini configuration error: {e}")
else:
    log("Warning: GEMINI_API_KEY not found")

# Read Skill Definition for System Prompt
SKILL_PATH = Path(".agent/skills/utils/prompt-lang-generator/SKILL.md")
SYSTEM_PROMPT = ""
try:
    if SKILL_PATH.exists():
        SYSTEM_PROMPT = SKILL_PATH.read_text(encoding="utf-8")
        log(f"Loaded System Prompt from {SKILL_PATH}")
    else:
        log(f"Skill definition not found at {SKILL_PATH}")
        SYSTEM_PROMPT = "You are a Prompt-Lang generator. Generate structured .prompt files."
except Exception as e:
    log(f"Error reading skill definition: {e}")

# Initialize Server
server = Server(
    name="prompt-lang-generator",
    version="1.0.0",
    instructions="Generate structured Prompt-Lang code from natural language requirements."
)

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="generate_prompt",
            description="Generate Prompt-Lang code from requirements.",
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
    log(f"call_tool: {name}")

    if name == "generate_prompt":
        req = arguments.get("requirements")
        if not req:
            return [TextContent(type="text", text="Error: requirements missing")]

        if not model:
             return [TextContent(type="text", text="Error: LLM not configured (GEMINI_API_KEY missing)")]

        try:
            # Construct Prompt
            # We append instructions to ensure only code is returned or code block is clear
            prompt = f"{SYSTEM_PROMPT}\n\n=== User Requirements ===\n{req}\n\n=== Instructions ===\nGenerate the .prompt content. Output only the code block if possible."

            log("Sending request to Gemini...")
            response = await model.generate_content_async(prompt)
            output = response.text
            log("Received response from Gemini")

            # Log for Meta-learning
            log_execution(req, output)

            return [TextContent(type="text", text=output)]
        except Exception as e:
            log(f"Generation error: {e}")
            return [TextContent(type="text", text=f"Error generating prompt: {str(e)}")]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    log("Starting stdio server...")
    try:
        async with stdio_server() as streams:
            log("stdio_server connected")
            await server.run(
                streams[0],
                streams[1],
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
