#!/usr/bin/env python3
"""
Prompt-Lang MCP Server
======================

Model Context Protocol server for prompt-lang-generator.
Exposes tools to generate Prompt-Lang v2.0 code from natural language requirements.

CRITICAL: This file follows MCP stdio protocol rules:
- stdout: JSON-RPC messages ONLY
- stderr: All logging and debug output
"""

import sys
import os
import json
import re

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

# ============ Import path setup ============
from pathlib import Path
REPO_ROOT = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(REPO_ROOT))
log(f"Repo root: {REPO_ROOT}")

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
        captured = self._null.getvalue()
        if captured.strip():
            log(f"Suppressed stdout during import: {captured[:100]}...")

# Import dependencies
try:
    with StdoutSuppressor():
        import yaml
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
    log("Imports successful")
except Exception as e:
    log(f"Import error: {e}")
    sys.exit(1)

# Initialize MCP server
server = Server(
    name="prompt-lang",
    version="1.0.0",
    instructions="Generate Prompt-Lang v2.0 code from natural language requirements"
)

# Template paths
TEMPLATE_DIR = REPO_ROOT / ".agent" / "skills" / "utils" / "prompt-lang-generator" / "templates"
DOMAIN_TEMPLATE_DIR = TEMPLATE_DIR / "domain_templates"

# ============ Logic ============

def load_template(path: Path) -> dict:
    """Load a YAML template."""
    if not path.exists():
        log(f"Template not found: {path}")
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        log(f"Error loading template {path}: {e}")
        return {}

def detect_domain(requirements: str) -> str | None:
    """Detect domain from requirements string."""
    req_lower = requirements.lower()

    # Simple keyword matching
    domains = {
        "technical": ["code", "api", "function", "class", "debug", "refactor", "java", "python", "script"],
        "rag": ["retrieval", "search", "document", "knowledge base", "query", "rag", "context"],
        "summarization": ["summarize", "summary", "abstract", "tl;dr", "shorten", "condense"]
    }

    for domain, keywords in domains.items():
        for kw in keywords:
            if kw in req_lower:
                return domain
    return None

def merge_templates(base: dict, domain_tmpl: dict) -> dict:
    """Merge domain template into base template."""
    merged = base.copy()

    # Merge constraints
    if "domain_constraints" in domain_tmpl:
        merged.setdefault("required", {}).setdefault("constraints", [])
        if isinstance(merged["required"]["constraints"], list):
            merged["required"]["constraints"].extend(domain_tmpl["domain_constraints"])

    # Merge rubric
    if "domain_rubric" in domain_tmpl:
        merged.setdefault("optional", {}).setdefault("rubric", [])
        if isinstance(merged["optional"]["rubric"], list):
            merged["optional"]["rubric"].extend(domain_tmpl["domain_rubric"])

    # Override format if domain specific
    if "domain_format" in domain_tmpl:
        merged.setdefault("required", {})["format"] = domain_tmpl["domain_format"]

    # Keep track of domain for metadata
    merged["_domain"] = domain_tmpl.get("domain", "unknown")

    return merged

def generate_prompt_lang_code(requirements: str, domain_hint: str = None) -> str:
    """Generate Prompt-Lang code from requirements."""
    log(f"Generating for: {requirements[:50]}...")

    # 1. Detect domain
    domain = domain_hint or detect_domain(requirements)
    log(f"Detected domain: {domain}")

    # 2. Load templates
    base_tmpl = load_template(TEMPLATE_DIR / "base_template.yaml")

    domain_tmpl = {}
    if domain:
        domain_path = DOMAIN_TEMPLATE_DIR / f"{domain}.yaml"
        domain_tmpl = load_template(domain_path)

    # 3. Merge
    data = merge_templates(base_tmpl, domain_tmpl)

    # 4. Construct Markdown output
    lines = []

    # Header
    name = "generated_skill" # Placeholder
    lines.append(f"#prompt {name}")
    lines.append("")

    # Role
    lines.append("@role:")
    lines.append(f"  {data.get('required', {}).get('role', '').strip() or 'AI Assistant'}")
    lines.append("")

    # Goal
    lines.append("@goal:")
    lines.append(f"  {requirements}") # Use input requirements as goal
    lines.append("")

    # Constraints
    lines.append("@constraints:")
    constraints = data.get("required", {}).get("constraints", [])
    # Filter out empty placeholders from template if they exist
    constraints = [c for c in constraints if c and isinstance(c, str)]
    if not constraints:
        constraints = ["Follow instructions carefully."]
    for c in constraints:
        lines.append(f"  - {c}")
    lines.append("")

    # Format
    lines.append("@format:")
    fmt = data.get("required", {}).get("format", "")
    if fmt:
        # Indent format block
        for line in fmt.strip().split("\n"):
            lines.append(f"  {line}")
    else:
        lines.append("  (Define output format here)")
    lines.append("")

    # Examples
    lines.append("@examples:")
    examples = data.get("required", {}).get("examples", [])
    if examples and isinstance(examples, list) and examples[0].get("input"):
        for ex in examples:
            lines.append(f"  - input: {ex.get('input', '')}")
            lines.append(f"    output: {ex.get('output', '')}")
    else:
         lines.append("  - input: (Example input)")
         lines.append("    output: (Example output)")
    lines.append("")

    # Rubric (Optional)
    rubric = data.get("optional", {}).get("rubric", [])
    if rubric:
        lines.append("@rubric:")
        for dim in rubric:
            lines.append(f"  - {dim.get('name', 'dimension')}:")
            lines.append(f"      description: {dim.get('description', '')}")
            lines.append(f"      scale: {dim.get('scale', '1-5')}")
            if "criteria" in dim:
                lines.append("      criteria:")
                for k, v in dim["criteria"].items():
                    lines.append(f"        {k}: {v}")
        lines.append("")

    return "\n".join(lines)

# ============ MCP Tools ============

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="generate",
            description="Generate Prompt-Lang v2.0 code from natural language requirements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "Natural language description of the skill or prompt requirements."
                    },
                    "domain": {
                        "type": "string",
                        "description": "Optional domain hint (technical, rag, summarization).",
                        "enum": ["technical", "rag", "summarization"]
                    }
                },
                "required": ["requirements"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "generate":
        requirements = arguments.get("requirements", "")
        domain = arguments.get("domain")

        if not requirements:
            return [TextContent(type="text", text="Error: requirements are required")]

        try:
            result = generate_prompt_lang_code(requirements, domain)
            return [TextContent(type="text", text=result)]
        except Exception as e:
            log(f"Generation error: {e}")
            return [TextContent(type="text", text=f"Error generating code: {str(e)}")]

    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

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
