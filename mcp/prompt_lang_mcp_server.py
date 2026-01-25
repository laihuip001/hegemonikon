#!/usr/bin/env python3
"""
Prompt-Lang MCP Server
======================

MCP server for generating Prompt-Lang v2.0 code from natural language requirements.
Part of Phase C integration.

Features:
- generate: Create .prompt files from requirements
- Automatic domain detection
- Template-based generation
- Execution logging for meta-learning
"""

import sys
import os
import json
import yaml
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# ============ CRITICAL: Platform-specific asyncio setup ============
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ============ CRITICAL: Redirect ALL stdout to stderr ============
import io
_original_stdout = sys.stdout
_stderr_wrapper = sys.stderr

def log(msg):
    """Log to stderr to avoid interfering with MCP stdio protocol."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] [prompt-lang-mcp] {msg}", file=sys.stderr, flush=True)

# ============ Import path setup ============
repo_root = Path(__file__).parent.parent.resolve()
prompt_lang_path = repo_root / "forge" / "prompt-lang"
sys.path.insert(0, str(prompt_lang_path))

try:
    from prompt_lang import Prompt, Rubric, RubricDimension, ContextItem, Activation
    log(f"Successfully imported prompt_lang from {prompt_lang_path}")
except ImportError as e:
    log(f"Failed to import prompt_lang: {e}")
    sys.exit(1)

# ============ Suppress stdout during imports ============
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

try:
    with StdoutSuppressor():
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
    log("MCP imports successful")
except ImportError as e:
    log(f"MCP import error: {e}. Please install 'mcp' package.")
    sys.exit(1)


# ============ Constants ============
SKILL_ROOT = repo_root / ".agent" / "skills" / "utils" / "prompt-lang-generator"
TEMPLATES_DIR = SKILL_ROOT / "templates"
LOGS_DIR = SKILL_ROOT / "logs"

# Ensure logs directory exists
LOGS_DIR.mkdir(parents=True, exist_ok=True)


# ============ Helper Functions ============

def load_yaml(path: Path) -> Dict[str, Any]:
    """Load a YAML file."""
    if not path.exists():
        log(f"Warning: Template not found at {path}")
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        log(f"Error loading YAML {path}: {e}")
        return {}

def detect_domain(requirements: str) -> str:
    """Detect domain from requirements text."""
    req_lower = requirements.lower()

    domains = {
        "technical": ["code", "refactor", "bug", "python", "javascript", "api", "database", "sql"],
        "rag": ["search", "retrieve", "knowledge base", "rag", "retrieval", "query", "answer"],
        "summarization": ["summarize", "digest", "tl;dr", "abstract", "summary"]
    }

    scores = {d: 0 for d in domains}
    for domain, keywords in domains.items():
        for kw in keywords:
            if kw in req_lower:
                scores[domain] += 1

    # Return domain with highest score if > 0
    best_domain = max(scores, key=scores.get)
    if scores[best_domain] > 0:
        return best_domain
    return "general"  # Default

def merge_templates(base: Dict, overlay: Dict) -> Dict:
    """Deep merge two template dictionaries."""
    result = base.copy()

    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_templates(result[key], value)
        else:
            result[key] = value

    return result

def template_to_prompt(data: Dict, requirements: str, name: str) -> Prompt:
    """Convert template data to Prompt object, filling placeholders."""

    # Helper to fill placeholders
    def fill(text: str) -> str:
        if not isinstance(text, str): return text
        return text.replace("{{requirements}}", requirements)

    required = data.get("required", {})
    optional = data.get("optional", {})

    # 1. Basic Fields
    prompt = Prompt(
        name=name,
        role=fill(required.get("role", "AI Assistant")),
        goal=fill(required.get("goal", requirements)),
        constraints=[fill(c) for c in required.get("constraints", [])],
        format=required.get("format", "Markdown"),
        examples=required.get("examples", [])
    )

    # 2. Rubric
    rubric_data = optional.get("rubric")
    if rubric_data:
        prompt.rubric = Rubric()
        for dim in rubric_data:
            # Handle list of dicts
            prompt.rubric.dimensions.append(RubricDimension(
                name=dim.get("name", "dimension"),
                description=dim.get("description", ""),
                scale=dim.get("scale", "1-5")
            ))

    # 3. Activation
    act_data = optional.get("activation")
    if act_data:
        prompt.activation = Activation(
            mode=act_data.get("mode", "manual"),
            pattern=act_data.get("pattern"),
            priority=act_data.get("priority", 1)
        )

    # 4. Context
    ctx_data = optional.get("context")
    if ctx_data:
        for item in ctx_data:
            prompt.context.append(ContextItem(
                ref_type=item.get("type", "file"),
                path=item.get("path", ""),
                priority=item.get("priority", "MEDIUM")
            ))

    # 5. Populate Role/Goal with user requirements if generic
    if not prompt.role or prompt.role.strip() == "":
        prompt.role = "AI Assistant specialized in the requested task."

    # Append requirements to goal to ensure specific instructions are preserved
    # If the template has a generic goal, we append the user requirements.
    prompt.goal = f"{prompt.goal}\n\nSpecific Requirements:\n{requirements}"

    return prompt

def log_execution(tool: str, input_data: Dict, result: str):
    """Log execution for meta-learning."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "tool": tool,
        "input": input_data,
        "result_length": len(result),
        "result_preview": result[:100]
    }

    log_file = LOGS_DIR / f"execution_{datetime.now().strftime('%Y%m%d')}.jsonl"
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception as e:
        log(f"Failed to write log: {e}")


# ============ Server Setup ============

server = Server(
    name="prompt-lang-generator",
    version="1.0.0",
    instructions="Generates Prompt-Lang v2.0 code from natural language requirements."
)

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="generate",
            description="Generate a .prompt file content from natural language requirements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "Natural language description of the desired skill/prompt."
                    },
                    "domain": {
                        "type": "string",
                        "description": "Optional domain hint (technical, rag, summarization). If omitted, auto-detected."
                    },
                    "name": {
                        "type": "string",
                        "description": "Name of the skill (snake_case). Defaults to 'generated_skill'."
                    }
                },
                "required": ["requirements"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "generate":
        reqs = arguments.get("requirements", "")
        domain = arguments.get("domain") or detect_domain(reqs)
        skill_name = arguments.get("name", "generated_skill")

        log(f"Generating skill '{skill_name}' for domain '{domain}'")

        # 1. Load Templates
        base_tmpl = load_yaml(TEMPLATES_DIR / "base_template.yaml")
        domain_tmpl = load_yaml(TEMPLATES_DIR / "domain_templates" / f"{domain}.yaml")

        if not base_tmpl:
            return [TextContent(type="text", text="Error: Base template missing.")]

        # 2. Merge
        merged_tmpl = merge_templates(base_tmpl, domain_tmpl)

        # 3. Create Prompt Object
        prompt = template_to_prompt(merged_tmpl, reqs, skill_name)

        # 4. Compile to String
        # We use a custom compile logic because prompt.compile() is for System Prompts,
        # but we want to generate the .prompt SOURCE CODE.
        # prompt_lang.py doesn't seem to have a 'dump' or 'to_source' method that produces .prompt format.
        # It has 'to_json' and 'compile' (AST -> System Prompt).

        # We need to implement a 'to_source' equivalent here to output valid .prompt code.
        # OR we check if 'expand' or similar does it.
        # Checking prompt_lang.py source again...
        # It has 'to_json'. 'expand' creates natural language prompt. 'compile' creates System Prompt.
        # It seems we need to construct the .prompt format manually from the object.

        source_code = generate_source_code(prompt)

        # 5. Log
        log_execution("generate", arguments, source_code)

        return [TextContent(type="text", text=source_code)]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

def generate_source_code(prompt: Prompt) -> str:
    """Generate .prompt source code from Prompt object."""
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
        # Check if format needs triple backticks
        if "```" not in prompt.format:
            lines.append("  ```")
            lines.append(f"  {prompt.format}")
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

    if prompt.rubric and prompt.rubric.dimensions:
        lines.append("@rubric:")
        for dim in prompt.rubric.dimensions:
            lines.append(f"  - {dim.name}:")
            lines.append(f"      description: \"{dim.description}\"")
            lines.append(f"      scale: {dim.scale}")
        lines.append("")

    if prompt.activation:
        lines.append("@activation:")
        lines.append(f"  mode: {prompt.activation.mode}")
        if prompt.activation.pattern:
            lines.append(f"  pattern: \"{prompt.activation.pattern}\"")
        lines.append(f"  priority: {prompt.activation.priority}")
        lines.append("")

    if prompt.context:
        lines.append("@context:")
        for ctx in prompt.context:
            opts = []
            if ctx.priority != "MEDIUM":
                opts.append(f"priority={ctx.priority}")
            # Simplified options generation
            opts_str = f" [{', '.join(opts)}]" if opts else ""
            lines.append(f"  - {ctx.ref_type}:\"{ctx.path}\"{opts_str}")
        lines.append("")

    return "\n".join(lines)

async def main():
    log("Starting Prompt-Lang MCP Server...")
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
        log("Server stopped")
    except Exception as e:
        log(f"Fatal error: {e}")
        sys.exit(1)
