#!/usr/bin/env python3
"""
Prompt-Lang MCP Server
======================

MCP server for generating Prompt-Lang v2.0 code from natural language requirements.
"""

import sys
import os
import yaml
import asyncio
from pathlib import Path
from typing import Optional

# ============ CRITICAL: Platform-specific asyncio setup ============
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ============ CRITICAL: Redirect ALL stdout to stderr ============
import io
_original_stdout = sys.stdout
_stderr_wrapper = sys.stderr

def log(msg):
    print(f"[prompt-lang-mcp] {msg}", file=sys.stderr, flush=True)

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

# Import MCP SDK
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    log("MCP imports successful")
except Exception as e:
    log(f"MCP import error: {e}")
    sys.exit(1)

# Import Google GenAI
try:
    with StdoutSuppressor():
        import google.generativeai as genai
except ImportError:
    log("google-generativeai not found. Generation will fail.")
    genai = None

# Initialize MCP server
server = Server(
    name="prompt-lang",
    version="1.0.0",
    instructions="Generate Prompt-Lang v2.0 skills from natural language requirements."
)

# Constants
TEMPLATE_DIR = Path(__file__).parent.parent / ".agent" / "skills" / "utils" / "prompt-lang-generator" / "templates"

def load_template(name: str) -> str:
    """Load a template file."""
    path = TEMPLATE_DIR / name
    if not path.exists():
        log(f"Template not found: {path}")
        return ""
    return path.read_text(encoding="utf-8")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="prompt_lang_generate",
            description="Generate Prompt-Lang code from natural language requirements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "Natural language requirements for the skill."
                    },
                    "domain": {
                        "type": "string",
                        "description": "Domain hint (technical, rag, summarization). Defaults to technical.",
                        "enum": ["technical", "rag", "summarization"]
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format (default: skill.md)",
                        "default": "skill.md"
                    }
                },
                "required": ["requirements"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name != "prompt_lang_generate":
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    requirements = arguments.get("requirements")
    domain = arguments.get("domain", "technical")
    output_format = arguments.get("output_format", "skill.md")

    if not requirements:
        return [TextContent(type="text", text="Error: requirements are required")]

    # Check API Key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return [TextContent(type="text", text="Error: GEMINI_API_KEY not found in environment.")]

    if not genai:
        return [TextContent(type="text", text="Error: google-generativeai library not installed.")]

    # Configure GenAI
    with StdoutSuppressor():
        genai.configure(api_key=api_key)

    # Load Templates
    base_template = load_template("base_template.yaml")
    domain_template = load_template(f"domain_templates/{domain}.yaml")

    if not base_template:
         return [TextContent(type="text", text="Error: Could not load base_template.yaml")]

    # Construct Prompt
    system_instruction = f"""
You are an expert Prompt Engineer specializing in Prompt-Lang v2.0.
Your task is to generate a high-quality Prompt-Lang skill definition based on the user's requirements.

Reference Standards:
- Use the provided Base Template as the structure.
- Incorporate the Domain Template guidelines.
- Ensure all required directives (@role, @goal, @constraints, @format, @examples) are present.
- Output ONLY the generated Prompt-Lang code (Markdown format). Do not wrap in ```markdown if possible, just raw text, or if you do wrap, I will extract it.
"""

    user_prompt = f"""
# Context
Base Template:
{base_template}

Domain Template ({domain}):
{domain_template}

# Requirements
{requirements}

# Output Format
Target format: {output_format}
"""

    try:
        model = genai.GenerativeModel(
            "gemini-2.0-flash",
            system_instruction=system_instruction
        )
        response = model.generate_content(
            contents=[user_prompt],
            generation_config=genai.types.GenerationConfig(
                temperature=0.2
            )
        )

        generated_text = response.text

        # Simple cleanup if wrapped in markdown block
        if generated_text.startswith("```"):
            lines = generated_text.splitlines()
            if lines[0].strip().startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            generated_text = "\n".join(lines)

        return [TextContent(type="text", text=generated_text)]

    except Exception as e:
        log(f"Generation error: {e}")
        return [TextContent(type="text", text=f"Error during generation: {str(e)}")]

async def main():
    log("Starting stdio server...")
    async with stdio_server() as streams:
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options()
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log("Server stopped by user")
    except Exception as e:
        log(f"Fatal error: {e}")
        sys.exit(1)
