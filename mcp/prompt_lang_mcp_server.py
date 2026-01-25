#!/usr/bin/env python3
"""
Prompt-Lang MCP Server
======================

MCP server for generating Prompt-Lang v2.0 code from natural language requirements.
Part of Phase C integration.

- Tool: prompt_lang_generate
"""

import sys
import os
import io
import re
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, List

# ============ CRITICAL: Platform-specific asyncio setup ============
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ============ CRITICAL: Redirect ALL stdout to stderr ============
_original_stdout = sys.stdout
_stderr_wrapper = sys.stderr

def log(msg):
    print(f"[prompt-lang-mcp] {msg}", file=sys.stderr, flush=True)

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

with StdoutSuppressor():
    try:
        import yaml
    except ImportError:
        log("Warning: pyyaml not installed. Template loading may fail.")
        yaml = None

    try:
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
    except ImportError as e:
        log(f"MCP import error: {e}")
        sys.exit(1)

# ============ Constants ============
REPO_ROOT = Path(__file__).parent.parent
TEMPLATE_DIR = REPO_ROOT / ".agent/skills/utils/prompt-lang-generator/templates"

# ============ Logic Class ============

class PromptLangGenerator:
    """Logic for generating Prompt-Lang code from templates."""

    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.base_template_path = template_dir / "base_template.yaml"
        self.domain_templates_dir = template_dir / "domain_templates"

    def detect_domain(self, requirements: str) -> str:
        """Detect domain from requirements using keyword matching."""
        req_lower = requirements.lower()

        domains = {
            "technical": ["code", "script", "python", "java", "ts", "js", "refactor", "bug", "api", "function", "class", "impl", "test", "review", "design pattern", "sql", "db", "server", "frontend", "backend"],
            "rag": ["retrieval", "search", "document", "knowledge base", "query", "context", "citation", "rag"],
            "summarization": ["summarize", "summary", "abstract", "tl;dr", "shorten", "condense", "key points"],
            "creative": ["story", "poem", "character", "plot", "dialogue"],
            "academic": ["paper", "thesis", "research", "citation", "bibliography"],
        }

        # Count matches
        scores = {}
        for domain, keywords in domains.items():
            count = sum(1 for kw in keywords if kw in req_lower)
            if count > 0:
                scores[domain] = count

        if not scores:
            return "general"

        # Return domain with highest score
        return max(scores.items(), key=lambda x: x[1])[0]

    def load_template(self, domain: str) -> Dict[str, Any]:
        """Load and merge base template with domain template."""
        if not yaml:
            raise ImportError("pyyaml is required to load templates")

        # Load base
        if not self.base_template_path.exists():
            log(f"Base template not found at {self.base_template_path}")
            return {}

        try:
            with open(self.base_template_path, 'r', encoding='utf-8') as f:
                base = yaml.safe_load(f)
        except Exception as e:
            log(f"Error loading base template: {e}")
            return {}

        # Load domain
        domain_path = self.domain_templates_dir / f"{domain}.yaml"
        if not domain_path.exists():
            log(f"Domain template not found for {domain}, using base only.")
            return base

        try:
            with open(domain_path, 'r', encoding='utf-8') as f:
                domain_tmpl = yaml.safe_load(f)
        except Exception as e:
            log(f"Error loading domain template: {e}")
            return base

        return self._merge_templates(base, domain_tmpl)

    def _merge_templates(self, base: Dict, domain: Dict) -> Dict:
        """Merge domain template into base template."""
        merged = base.copy()

        # Merge optional sections if they exist
        if "domain_constraints" in domain:
            # Add to base constraints (which is a list in base['required']['constraints'])
            if "required" in merged and "constraints" in merged["required"]:
                 # Ensure base constraints is a list (template might have sample list)
                 current = merged["required"]["constraints"]
                 if isinstance(current, list):
                     merged["required"]["constraints"] = current + domain["domain_constraints"]

        if "domain_rubric" in domain:
            if "optional" in merged:
                if "rubric" not in merged["optional"]:
                    merged["optional"]["rubric"] = []
                # Append or replace? Let's append
                if isinstance(merged["optional"]["rubric"], list):
                    merged["optional"]["rubric"].extend(domain["domain_rubric"])

        if "domain_format" in domain:
            if "required" in merged:
                merged["required"]["format"] = domain["domain_format"]

        return merged

    def render_prompt(self, template: Dict, requirements: str, domain: str) -> str:
        """Render the final Prompt-Lang string."""
        lines = []

        # Header
        slug = re.sub(r'[^a-z0-9_]', '_', domain.lower())
        lines.append(f"#prompt {slug}_skill")
        lines.append("")

        # Helper to get value safe
        def get_val(path_list, default=""):
            curr = template
            for key in path_list:
                if isinstance(curr, dict) and key in curr:
                    curr = curr[key]
                else:
                    return default
            return curr

        # Role
        lines.append("@role:")
        role_tmpl = get_val(["required", "role"])
        lines.append(f"  {role_tmpl.strip()}")
        lines.append(f"  <!-- TODO: Define specific role based on: {requirements[:50]}... -->")
        lines.append("")

        # Goal
        lines.append("@goal:")
        goal_tmpl = get_val(["required", "goal"])
        lines.append(f"  {goal_tmpl.strip()}")
        lines.append(f"  <!-- TODO: Achieve: {requirements} -->")
        lines.append("")

        # Constraints
        lines.append("@constraints:")
        constraints = get_val(["required", "constraints"], [])
        for c in constraints:
            if c:
                lines.append(f"  - {c}")
        lines.append(f"  - <!-- TODO: Add constraint for {requirements[:30]}... -->")
        lines.append("")

        # Format
        lines.append("@format:")
        fmt = get_val(["required", "format"])
        for line in fmt.split("\n"):
            lines.append(f"  {line}")
        lines.append("")

        # Examples
        lines.append("@examples:")
        examples = get_val(["required", "examples"], [])
        for ex in examples:
            lines.append(f"  - input: {ex.get('input', '')}")
            lines.append(f"    output: {ex.get('output', '')}")
        lines.append("")

        # Rubric
        rubric = get_val(["optional", "rubric"])
        if rubric:
            lines.append("@rubric:")
            for item in rubric:
                lines.append(f"  - {item['name']}:")
                lines.append(f"      description: {item.get('description', '')}")
                lines.append(f"      scale: {item.get('scale', '1-5')}")
                if "criteria" in item:
                    lines.append("      criteria:")
                    for k, v in item["criteria"].items():
                        lines.append(f"        {k}: {v}")
            lines.append("")

        return "\n".join(lines)

# ============ Server Setup ============

server = Server(
    name="prompt-lang-generator",
    version="1.0.0",
    instructions="Generate Prompt-Lang v2.0 code from requirements"
)

generator = PromptLangGenerator(TEMPLATE_DIR)

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="generate",
            description="Generate Prompt-Lang code from natural language requirements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "Natural language description of the desired skill/prompt."
                    },
                    "domain": {
                        "type": "string",
                        "description": "Optional domain hint (technical, rag, summarization, etc.). If omitted, auto-detected."
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format (default: 'skill.md'). Currently only returns raw Prompt-Lang code."
                    }
                },
                "required": ["requirements"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name != "generate":
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    requirements = arguments.get("requirements", "")
    domain = arguments.get("domain")

    if not requirements:
        return [TextContent(type="text", text="Error: requirements are required")]

    if not domain:
        domain = generator.detect_domain(requirements)
        log(f"Detected domain: {domain}")

    try:
        template = generator.load_template(domain)
        result = generator.render_prompt(template, requirements, domain)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        log(f"Generation error: {e}")
        return [TextContent(type="text", text=f"Error generating prompt: {e}")]

async def main():
    log("Starting prompt-lang-mcp server...")
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
