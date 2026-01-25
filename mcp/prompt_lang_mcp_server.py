#!/usr/bin/env python3
"""
Prompt-Lang MCP Server
======================

MCP server for generating Prompt-Lang v2.0 code from natural language requirements.
"""

import sys
import os
import json
from pathlib import Path

# Platform-specific asyncio setup
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Redirect stdout to stderr for logging, as MCP uses stdout for communication
_original_stdout = sys.stdout
_stderr_wrapper = sys.stderr

def log(msg):
    print(f"[prompt-lang-mcp] {msg}", file=sys.stderr, flush=True)

# Path setup to import forge
# Assuming we are in mcp/ directory, forge is in ../forge
REPO_ROOT = Path(__file__).parent.parent
FORGE_PATH = REPO_ROOT / "forge" / "prompt-lang"
sys.path.insert(0, str(FORGE_PATH))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
    # Attempt to import Prompt class
    try:
        from prompt_lang import Prompt
        log("Imported Prompt class successfully")
    except ImportError:
        log("Failed to import Prompt class from prompt_lang. Using mock.")
        # Mock Prompt class if import fails (fallback)
        from dataclasses import dataclass, field
        from typing import List, Optional, Dict
        @dataclass
        class Prompt:
            name: str
            role: Optional[str] = None
            goal: Optional[str] = None
            constraints: List[str] = field(default_factory=list)
            format: Optional[str] = None
            examples: List[dict] = field(default_factory=list)
            tools: Dict[str, str] = field(default_factory=dict)
            resources: Dict[str, str] = field(default_factory=dict)
            rubric: Optional[object] = None
            conditions: List[object] = field(default_factory=list)
            activation: Optional[object] = None
            context: List[object] = field(default_factory=list)

except Exception as e:
    log(f"Setup error: {e}")
    sys.exit(1)

server = Server(
    name="prompt-lang-generator",
    version="1.0.0",
    instructions="Generate Prompt-Lang code from requirements"
)

# Hardcoded default template to avoid yaml dependency
DEFAULT_TEMPLATE = {
    "role": "AI Assistant",
    "constraints": [
        "Be helpful and harmless",
        "Follow the user's instructions precisely"
    ],
    "format": "```json\n{}\n```",
    "examples": [{"input": "Example Input", "output": "Example Output"}]
}

def generate_prompt_object(requirements, domain=None):
    # Heuristics to fill content
    role = DEFAULT_TEMPLATE["role"]
    if domain:
        role = f"{domain.capitalize()} Expert"
        if domain == "technical":
            role = "Senior Software Engineer"
        elif domain == "rag":
            role = "Knowledge Retrieval Specialist"

    goal = requirements

    constraints = list(DEFAULT_TEMPLATE["constraints"])
    if domain == "technical":
        constraints.append("Follow clean code practices")
        constraints.append("Ensure error handling")

    prompt = Prompt(
        name="generated_skill",
        role=role,
        goal=goal,
        constraints=constraints,
        format=DEFAULT_TEMPLATE["format"],
        examples=DEFAULT_TEMPLATE["examples"]
    )

    return prompt

def serialize_to_prompt_lang(prompt: Prompt) -> str:
    lines = []
    lines.append(f"#prompt {prompt.name}")
    lines.append("")

    if prompt.role:
        lines.append("@role:")
        for line in prompt.role.split('\n'):
            lines.append(f"  {line}")
        lines.append("")

    if prompt.goal:
        lines.append("@goal:")
        for line in prompt.goal.split('\n'):
            lines.append(f"  {line}")
        lines.append("")

    if prompt.constraints:
        lines.append("@constraints:")
        for c in prompt.constraints:
            lines.append(f"  - {c}")
        lines.append("")

    if prompt.format:
        lines.append("@format:")
        # Check if already fenced
        if "```" not in prompt.format:
             lines.append("  ```")
             for line in prompt.format.split('\n'):
                 lines.append(f"  {line}")
             lines.append("  ```")
        else:
             for line in prompt.format.split('\n'):
                 lines.append(f"  {line}")
        lines.append("")

    if prompt.examples:
        lines.append("@examples:")
        for ex in prompt.examples:
            lines.append(f"  - input: {ex.get('input', '')}")
            lines.append(f"    output: {ex.get('output', '')}")
        lines.append("")

    return "\n".join(lines)

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="generate",
            description="Generate Prompt-Lang code from natural language requirements",
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {"type": "string"},
                    "domain": {"type": "string", "description": "e.g. technical, rag, summarization"},
                    "output_format": {"type": "string", "default": "skill.md"}
                },
                "required": ["requirements"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    log(f"call_tool: {name} with {arguments}")
    if name == "generate":
        req = arguments.get("requirements")
        domain = arguments.get("domain")

        prompt_obj = generate_prompt_object(req, domain)
        source_code = serialize_to_prompt_lang(prompt_obj)

        return [TextContent(type="text", text=source_code)]

    return [TextContent(type="text", text=f"Unknown tool: {name}")]

async def main():
    async with stdio_server() as streams:
        log("Server started")
        await server.run(streams[0], streams[1], server.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(main())
    except Exception as e:
        log(f"Fatal: {e}")
