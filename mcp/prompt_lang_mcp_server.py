#!/usr/bin/env python3
"""
Prompt-Lang MCP Server
======================

Model Context Protocol server for Prompt-Lang generation.
Exposes tools to generate structured prompt definitions from natural language requirements.

CRITICAL: This file follows MCP stdio protocol rules:
- stdout: JSON-RPC messages ONLY
- stderr: All logging and debug output
"""

import sys
import os
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

# ============ CRITICAL: Platform-specific asyncio setup ============
# Must be done BEFORE any other imports that might use asyncio
if sys.platform == 'win32':
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ============ CRITICAL: Redirect ALL stdout to stderr ============
# This prevents any accidental stdout pollution from imported modules
import io
_original_stdout = sys.stdout
_stderr_wrapper = sys.stderr

# Debug logging to stderr (won't interfere with MCP stdio)
def log(msg):
    print(f"[prompt-lang-mcp] {msg}", file=sys.stderr, flush=True)

log("Starting Prompt-Lang MCP Server...")
log(f"Python: {sys.executable}")

# ============ Import path setup ============
sys.path.insert(0, str(Path(__file__).parent.parent))

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

# Import MCP SDK
try:
    with StdoutSuppressor():
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        from mcp.types import Tool, TextContent
    log("MCP imports successful")
except ImportError as e:
    log(f"MCP import error: {e}")
    # Fallback for development if mcp is not installed, but usually it should be
    # For now, we'll exit if not found
    sys.exit(1)

# Initialize MCP server
server = Server(
    name="prompt-lang",
    version="1.0.0",
    instructions="Generate Prompt-Lang v2.0 structured prompts from natural language requirements."
)

class SimpleYamlParser:
    """
    A simple parser for the specific subset of YAML used in Prompt-Lang templates.
    Handles:
    - Key-value pairs
    - Nested dictionaries (indentation based)
    - Multiline strings (value starting with |)
    - Lists (lines starting with -)
    """
    def __init__(self, content: str):
        self.lines = content.splitlines()
        self.pos = 0

    def parse(self) -> Dict[str, Any]:
        result = {}
        while self.pos < len(self.lines):
            line = self.lines[self.pos]
            stripped = line.strip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                self.pos += 1
                continue

            # Check indentation level (assuming 2 spaces per level)
            indent = len(line) - len(line.lstrip())
            if indent > 0:
                # Top level parse should not encounter indented lines unless handled by recursive calls
                self.pos += 1
                continue

            if ':' in stripped:
                key, value = stripped.split(':', 1)
                key = key.strip()
                value = value.strip()

                if value == '|':
                    # Multiline string
                    result[key] = self._parse_multiline_string(indent + 2)
                elif not value:
                    # Nested object or list
                    result[key] = self._parse_nested(indent + 2)
                else:
                    # Simple value
                    result[key] = value.strip('"\'')

                # Check if we didn't advance in _parse_nested (e.g. empty block)
                if self.pos < len(self.lines) and self.lines[self.pos] == line:
                     self.pos += 1
            else:
                self.pos += 1
        return result

    def _parse_multiline_string(self, min_indent: int) -> str:
        self.pos += 1 # Skip the '|' line
        lines = []
        while self.pos < len(self.lines):
            line = self.lines[self.pos]
            if not line.strip(): # Keep empty lines
                lines.append("")
                self.pos += 1
                continue

            indent = len(line) - len(line.lstrip())
            if indent < min_indent:
                break

            # Remove base indent
            lines.append(line[min_indent:])
            self.pos += 1
        return "\n".join(lines).strip()

    def _parse_nested(self, min_indent: int):
        # Determine if it's a list or dict based on the first item
        # Look ahead for first non-empty line
        lookahead_pos = self.pos + 1
        while lookahead_pos < len(self.lines):
            line = self.lines[lookahead_pos]
            if line.strip() and not line.strip().startswith('#'):
                indent = len(line) - len(line.lstrip())
                if indent < min_indent:
                    return {} # Empty block

                if line.strip().startswith('-'):
                    return self._parse_list(min_indent)
                else:
                    return self._parse_dict(min_indent)
            lookahead_pos += 1
        return {} # End of file

    def _parse_list(self, min_indent: int) -> List[Any]:
        self.pos += 1 # Skip parent key line
        result = []
        while self.pos < len(self.lines):
            line = self.lines[self.pos]
            stripped = line.strip()

            if not stripped or stripped.startswith('#'):
                self.pos += 1
                continue

            indent = len(line) - len(line.lstrip())
            if indent < min_indent:
                break

            if stripped.startswith('-'):
                # Start of a new item
                content = stripped[1:].strip()
                if not content:
                    # "-": Block item (not used in current templates but standard yaml)
                    self.pos += 1
                elif ':' in content:
                     # It's a dict item starting on this line: "- key: val"
                     # We need to parse this and subsequent lines as a block

                     # Slurp lines until we hit next '-' at same indent or lower indent
                     item_lines = [line.replace('-', ' ', 1)] # Replace first - with space

                     current_item_indent = indent
                     idx = self.pos + 1
                     while idx < len(self.lines):
                         next_line = self.lines[idx]
                         next_stripped = next_line.strip()

                         if not next_stripped or next_stripped.startswith('#'):
                             idx += 1
                             continue

                         next_indent = len(next_line) - len(next_line.lstrip())
                         if next_indent < current_item_indent:
                             break # End of list
                         if next_indent == current_item_indent and next_stripped.startswith('-'):
                             break # Next item

                         item_lines.append(next_line)
                         idx += 1

                     # Parse the block
                     dedented_block = self._dedent_block(item_lines)
                     sub_parser = SimpleYamlParser(dedented_block)
                     result.append(sub_parser.parse())

                     self.pos = idx
                     continue

                else:
                    # Simple string item
                    val = content.strip().strip('"\'')
                    result.append(val)
                    self.pos += 1
            else:
                 # Should have been consumed by list item logic above or continuation of previous item (not supported for string items)
                 self.pos += 1
        return result

    def _dedent_block(self, lines: List[str]) -> str:
        if not lines: return ""
        # Find min indent of non-empty lines
        indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
        if not indents: return ""
        min_indent = min(indents)
        return "\n".join(line[min_indent:] for line in lines)

    def _parse_dict(self, min_indent: int) -> Dict[str, Any]:
        self.pos += 1 # Skip parent key line
        result = {}
        while self.pos < len(self.lines):
            line = self.lines[self.pos]
            stripped = line.strip()

            if not stripped or stripped.startswith('#'):
                self.pos += 1
                continue

            indent = len(line) - len(line.lstrip())
            if indent < min_indent:
                break

            if ':' in stripped:
                key, value = stripped.split(':', 1)
                key = key.strip()
                value = value.strip()

                if value == '|':
                    result[key] = self._parse_multiline_string(indent + 2)
                elif not value:
                    # Recursive nested
                    result[key] = self._parse_nested(indent + 2)
                else:
                    result[key] = value.strip('"\'')

                # Ensure we advance if we haven't already (e.g. simple value or empty nested)
                if self.pos < len(self.lines) and self.lines[self.pos] == line:
                    self.pos += 1
            else:
                self.pos += 1
        return result

class PromptGenerator:
    # Resolve path relative to this script file to ensure it works from anywhere
    TEMPLATE_DIR = Path(__file__).parent.parent / ".agent/skills/utils/prompt-lang-generator/templates"

    def __init__(self):
        pass

    def load_template(self, name: str) -> Dict[str, Any]:
        if name == "base":
            path = self.TEMPLATE_DIR / "base_template.yaml"
        else:
            path = self.TEMPLATE_DIR / "domain_templates" / f"{name}.yaml"

        if not path.exists():
            log(f"Template not found: {path}")
            return {}

        try:
            content = path.read_text(encoding='utf-8')
            return SimpleYamlParser(content).parse()
        except Exception as e:
            log(f"Error loading template {name}: {e}")
            return {}

    def detect_domain(self, requirements: str) -> str:
        req_lower = requirements.lower()
        if any(w in req_lower for w in ["code", "refactor", "bug", "technical", "api", "system", "script", "function", "class", "impl"]):
            return "technical"
        if any(w in req_lower for w in ["search", "retrieval", "rag", "knowledge", "citation", "paper", "document", "info", "find", "query"]):
            return "rag"
        if any(w in req_lower for w in ["summary", "summarize", "abstract", "digest", "brief", "tl;dr"]):
            return "summarization"
        return "general"

    def merge_templates(self, base: Dict, domain: Dict) -> Dict:
        merged = base.copy()

        # Helper to get nested
        def get_nested(d, *keys):
            curr = d
            for k in keys:
                if isinstance(curr, dict) and k in curr:
                    curr = curr[k]
                else:
                    return None
            return curr

        # Merge constraints
        base_constraints = get_nested(base, "required", "constraints") or []
        domain_constraints = domain.get("domain_constraints", [])
        if isinstance(base_constraints, list) and isinstance(domain_constraints, list):
             # Update base['required']['constraints'] effectively
             # Since it's deep nested, we need to ensure structure exists
             if "required" not in merged: merged["required"] = {}
             if "constraints" not in merged["required"]: merged["required"]["constraints"] = []
             merged["required"]["constraints"] = base_constraints + domain_constraints

        # Merge rubric
        base_rubric = get_nested(base, "optional", "rubric") or []
        domain_rubric = domain.get("domain_rubric", [])
        if isinstance(base_rubric, list) and isinstance(domain_rubric, list):
             if "optional" not in merged: merged["optional"] = {}
             if "rubric" not in merged["optional"]: merged["optional"]["rubric"] = []
             merged["optional"]["rubric"] = base_rubric + domain_rubric

        # Override format if domain_format exists
        if "domain_format" in domain:
            if "required" not in merged: merged["required"] = {}
            merged["required"]["format"] = domain["domain_format"]

        return merged

    def construct_prompt(self, template: Dict, requirements: str, domain_name: str) -> str:
        # Extract parts
        role = template.get("required", {}).get("role", "[INSERT ROLE]")
        goal = template.get("required", {}).get("goal", "[INSERT GOAL]")
        constraints = template.get("required", {}).get("constraints", [])
        fmt = template.get("required", {}).get("format", "```\n[INSERT FORMAT]\n```")
        examples = template.get("required", {}).get("examples", [])
        rubric = template.get("optional", {}).get("rubric", [])

        # Build output
        parts = []
        parts.append(f"#prompt generated_{domain_name}_skill")

        parts.append(f"\n@role:\n  {role.replace(chr(10), chr(10)+'  ')}")

        # Inject requirements into goal
        goal_text = goal
        if requirements:
            goal_text += f"\n\n    User Requirements:\n    {requirements.replace(chr(10), chr(10)+'    ')}"
        parts.append(f"\n@goal:\n  {goal_text.replace(chr(10), chr(10)+'  ')}")

        if constraints:
            parts.append("\n@constraints:")
            for c in constraints:
                parts.append(f"  - {c}")

        parts.append(f"\n@format:\n{fmt}")

        if rubric:
            parts.append("\n@rubric:")
            for r in rubric:
                if isinstance(r, dict):
                    # Handle both simple dict and parsed structure
                    # Our parser returns dicts for list items usually
                    # Check structure based on technical.yaml
                    # - name: "correctness" ...
                    name = r.get("name", "dimension")
                    desc = r.get("description", "")
                    scale = r.get("scale", "1-5")
                    parts.append(f"  - {name}:")
                    parts.append(f"      description: {desc}")
                    parts.append(f"      scale: {scale}")

                    criteria = r.get("criteria")
                    if criteria and isinstance(criteria, dict):
                        parts.append("      criteria:")
                        for score, crit_desc in criteria.items():
                             parts.append(f"        {score}: {crit_desc}")

        if examples:
            parts.append("\n@examples:")
            for ex in examples:
                if isinstance(ex, dict):
                    inp = ex.get("input", "")
                    out = ex.get("output", "")
                    parts.append(f"  - input: {inp}")
                    parts.append(f"    output: {out}")

        return "\n".join(parts)

generator = PromptGenerator()

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="generate",
            description="Generate a Prompt-Lang v2.0 structured prompt definition from natural language requirements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "requirements": {
                        "type": "string",
                        "description": "Natural language description of the desired skill or prompt."
                    },
                    "domain": {
                        "type": "string",
                        "description": "Optional domain hint (technical, rag, summarization). If not provided, it will be inferred.",
                        "enum": ["technical", "rag", "summarization", "general"]
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format (default: skill.md). Currently returns raw prompt-lang code.",
                        "default": "skill.md"
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

        if not domain:
            domain = generator.detect_domain(requirements)

        log(f"Generating prompt for domain: {domain}")

        base_tmpl = generator.load_template("base")
        if not base_tmpl:
            return [TextContent(type="text", text="Error: Could not load base template.")]

        if domain != "general":
            domain_tmpl = generator.load_template(domain)
            merged = generator.merge_templates(base_tmpl, domain_tmpl)
        else:
            merged = base_tmpl

        result = generator.construct_prompt(merged, requirements, domain)

        return [TextContent(type="text", text=result)]

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
