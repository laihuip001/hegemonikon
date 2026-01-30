# PROOF: [L2/インフラ] S2→プロンプト言語が必要→prompt_lang が担う
#!/usr/bin/env python3
"""
prompt-lang Parser
==================

Parse .prompt files into structured data.

Usage:
    python prompt_lang.py parse <file>       # Parse and output JSON
    python prompt_lang.py validate <file>    # Validate syntax
    python prompt_lang.py expand <file>      # Expand to natural language prompt

Requirements:
    Python 3.10+
"""

import re
import json
import sys
import asyncio
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class PromptBlock:
    """A single block in a prompt-lang file."""
    block_type: str
    content: str | list | dict


@dataclass
class RubricDimension:
    """A single rubric dimension for evaluation."""
    name: str
    description: str
    scale: str  # "1-5", "1-10", "binary", "percent"
    criteria: dict[str, str] = field(default_factory=dict)


@dataclass
class Rubric:
    """Rubric block for self-evaluation."""
    dimensions: list[RubricDimension] = field(default_factory=list)
    output_format: Optional[str] = None
    output_key: Optional[str] = None


@dataclass
class Condition:
    """Conditional block (@if/@else)."""
    variable: str
    operator: str  # "==", "!=", ">", "<", ">=", "<="
    value: str
    if_content: dict = field(default_factory=dict)
    else_content: dict = field(default_factory=dict)


@dataclass
class Activation:
    """Activation metadata for glob/rule integration."""
    mode: str = "manual"  # "always_on", "manual", "glob", "model_decision"
    pattern: Optional[str] = None
    priority: int = 1
    rules: list[str] = field(default_factory=list)


@dataclass
class ContextItem:
    """A single context resource reference."""
    ref_type: str  # "file", "dir", "conv", "mcp", "ki"
    path: str
    priority: str = "MEDIUM"  # "HIGH", "MEDIUM", "LOW"
    section: Optional[str] = None
    filter: Optional[str] = None
    depth: Optional[int] = None
    tool_chain: Optional[str] = None


# v2.1 additions
@dataclass
class Mixin:
    """Reusable template fragment for composition."""
    name: str
    role: Optional[str] = None
    goal: Optional[str] = None
    constraints: list[str] = field(default_factory=list)
    format: Optional[str] = None
    examples: list[dict] = field(default_factory=list)
    tools: dict[str, str] = field(default_factory=dict)
    resources: dict[str, str] = field(default_factory=dict)
    rubric: Optional['Rubric'] = None
    activation: Optional[Activation] = None
    context: list[ContextItem] = field(default_factory=list)


class CircularReferenceError(Exception):
    """Error when circular reference is detected in extends/mixin chain."""
    def __init__(self, chain: list[str]):
        self.chain = chain
        super().__init__(f"Circular reference: {' → '.join(chain)}")


class ReferenceError(Exception):
    """Error when referenced prompt/mixin is not found."""
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Reference not found: {name}")


@dataclass
class Prompt:
    """Parsed prompt-lang document."""
    name: str
    role: Optional[str] = None
    goal: Optional[str] = None
    constraints: list[str] = field(default_factory=list)
    format: Optional[str] = None
    examples: list[dict] = field(default_factory=list)
    tools: dict[str, str] = field(default_factory=dict)
    resources: dict[str, str] = field(default_factory=dict)
    # v2 additions
    rubric: Optional[Rubric] = None
    conditions: list[Condition] = field(default_factory=list)
    activation: Optional[Activation] = None
    # v2.0.1 additions
    context: list[ContextItem] = field(default_factory=list)
    # v2.1 additions (extends/mixin)
    extends: Optional[str] = None
    mixins: list[str] = field(default_factory=list)
    _resolved: bool = field(default=False, repr=False)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {k: v for k, v in asdict(self).items() if v}
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
    
    def expand(self) -> str:
        """Expand to natural language prompt."""
        parts = []
        
        if self.role:
            parts.append(f"You are {self.role.strip()}.")
        
        if self.goal:
            parts.append(f"\nYour task: {self.goal.strip()}")
        
        if self.tools:
            parts.append("\n\nAvailable tools:")
            for name, desc in self.tools.items():
                parts.append(f"- {name}: {desc}")
        
        if self.resources:
            parts.append("\n\nAvailable resources:")
            for name, uri in self.resources.items():
                parts.append(f"- {name}: {uri}")
        
        if self.constraints:
            parts.append("\n\nConstraints:")
            for c in self.constraints:
                parts.append(f"- {c}")
        
        if self.format:
            parts.append(f"\n\nOutput format:\n{self.format.strip()}")
        
        if self.examples:
            parts.append("\n\nExamples:")
            for ex in self.examples:
                parts.append(f"- Input: {ex.get('input', '')}")
                parts.append(f"  Output: {ex.get('output', '')}")
        
        # v2 additions
        if self.rubric and self.rubric.dimensions:
            parts.append("\n\nEvaluation Rubric:")
            for dim in self.rubric.dimensions:
                parts.append(f"- {dim.name}: {dim.description} (scale: {dim.scale})")
                if dim.criteria:
                    for score, desc in dim.criteria.items():
                        parts.append(f"    {score}: {desc}")
        
        if self.conditions:
            parts.append("\n\nConditional Rules:")
            for cond in self.conditions:
                parts.append(f"- When {cond.variable} {cond.operator} {cond.value}:")
                if cond.if_content.get("raw"):
                    parts.append(f"    {cond.if_content['raw'][:100]}...")
        
        return "\n".join(parts)
    
    def compile(self, context: dict = None, format: str = "markdown") -> str:
        """
        Compile AST to system prompt string.
        
        Args:
            context: Variables for @if evaluation (e.g., {"env": "prod"})
            format: Output format ("markdown", "xml", "plain")
        
        Returns:
            Compiled system prompt string
        """
        context = context or {}
        sections = []
        
        # Header
        sections.append(f"# {self.name}")
        
        # Role
        if self.role:
            sections.append(f"\n## Role\n{self.role.strip()}")
        
        # Goal
        if self.goal:
            sections.append(f"\n## Goal\n{self.goal.strip()}")
        
        # Context (v2.0.1) - with actual file reading
        if self.context:
            context_parts = ["\n## Context"]
            for item in self.context:
                context_parts.append(f"\n### [{item.ref_type}] {item.path}")
                context_parts.append(f"*Priority: {item.priority}*")
                
                # Resolve context based on type
                content = self._resolve_context_item(item)
                if content:
                    context_parts.append(f"```\n{content}\n```")
                else:
                    context_parts.append("<!-- Resource not available -->")
            sections.append("\n".join(context_parts))
        
        # Constraints
        if self.constraints:
            sections.append("\n## Constraints")
            for c in self.constraints:
                sections.append(f"- {c}")
        
        # Conditions (v2 - evaluated)
        if self.conditions:
            for cond in self.conditions:
                if self._evaluate_condition(cond, context):
                    # Use if_content
                    if cond.if_content.get("raw"):
                        sections.append(f"\n## Conditional (when {cond.variable}={cond.value})")
                        sections.append(cond.if_content["raw"])
                else:
                    # Use else_content
                    if cond.else_content.get("raw"):
                        sections.append(f"\n## Conditional (else)")
                        sections.append(cond.else_content["raw"])
        
        # Tools
        if self.tools:
            sections.append("\n## Available Tools")
            for name, desc in self.tools.items():
                sections.append(f"- **{name}**: {desc}")
        
        # Resources
        if self.resources:
            sections.append("\n## Resources")
            for name, uri in self.resources.items():
                sections.append(f"- **{name}**: {uri}")
        
        # Format
        if self.format:
            sections.append(f"\n## Output Format\n```\n{self.format.strip()}\n```")
        
        # Examples
        if self.examples:
            sections.append("\n## Examples")
            for i, ex in enumerate(self.examples, 1):
                sections.append(f"\n### Example {i}")
                if ex.get("input"):
                    sections.append(f"**Input**: {ex['input']}")
                if ex.get("output"):
                    sections.append(f"**Output**: {ex['output']}")
        
        # Rubric (v2)
        if self.rubric and self.rubric.dimensions:
            sections.append("\n## Evaluation Rubric")
            sections.append("| Dimension | Description | Scale |")
            sections.append("|:---|:---|:---|")
            for dim in self.rubric.dimensions:
                sections.append(f"| {dim.name} | {dim.description} | {dim.scale} |")
        
        return "\n".join(sections)

    async def compile_async(self, context: dict = None, mcp_handler=None, format: str = "markdown") -> str:
        """
        Async compile AST to system prompt string.

        Args:
            context: Variables for @if evaluation
            mcp_handler: Async callback for MCP resolution
            format: Output format
        """
        context = context or {}
        sections = []

        # Header
        sections.append(f"# {self.name}")

        # Role
        if self.role:
            sections.append(f"\n## Role\n{self.role.strip()}")

        # Goal
        if self.goal:
            sections.append(f"\n## Goal\n{self.goal.strip()}")

        # Context (v2.0.1) - with async resolution
        if self.context:
            context_parts = ["\n## Context"]
            for item in self.context:
                context_parts.append(f"\n### [{item.ref_type}] {item.path}")
                context_parts.append(f"*Priority: {item.priority}*")

                # Resolve context based on type
                if item.ref_type == "mcp":
                    content = await self._resolve_context_item_async(item, mcp_handler)
                else:
                    content = self._resolve_context_item(item)

                if content:
                    context_parts.append(f"```\n{content}\n```")
                else:
                    context_parts.append("<!-- Resource not available -->")
            sections.append("\n".join(context_parts))

        # Constraints
        if self.constraints:
            sections.append("\n## Constraints")
            for c in self.constraints:
                sections.append(f"- {c}")

        # Conditions (v2 - evaluated)
        if self.conditions:
            for cond in self.conditions:
                if self._evaluate_condition(cond, context):
                    # Use if_content
                    if cond.if_content.get("raw"):
                        sections.append(f"\n## Conditional (when {cond.variable}={cond.value})")
                        sections.append(cond.if_content["raw"])
                else:
                    # Use else_content
                    if cond.else_content.get("raw"):
                        sections.append(f"\n## Conditional (else)")
                        sections.append(cond.else_content["raw"])

        # Tools
        if self.tools:
            sections.append("\n## Available Tools")
            for name, desc in self.tools.items():
                sections.append(f"- **{name}**: {desc}")

        # Resources
        if self.resources:
            sections.append("\n## Resources")
            for name, uri in self.resources.items():
                sections.append(f"- **{name}**: {uri}")

        # Format
        if self.format:
            sections.append(f"\n## Output Format\n```\n{self.format.strip()}\n```")

        # Examples
        if self.examples:
            sections.append("\n## Examples")
            for i, ex in enumerate(self.examples, 1):
                sections.append(f"\n### Example {i}")
                if ex.get("input"):
                    sections.append(f"**Input**: {ex['input']}")
                if ex.get("output"):
                    sections.append(f"**Output**: {ex['output']}")

        # Rubric (v2)
        if self.rubric and self.rubric.dimensions:
            sections.append("\n## Evaluation Rubric")
            sections.append("| Dimension | Description | Scale |")
            sections.append("|:---|:---|:---|")
            for dim in self.rubric.dimensions:
                sections.append(f"| {dim.name} | {dim.description} | {dim.scale} |")

        return "\n".join(sections)

    async def _resolve_context_item_async(self, item: 'ContextItem', mcp_handler) -> Optional[str]:
        """Resolve a context item asynchronously."""
        if item.ref_type == "mcp":
            if not mcp_handler:
                return f"Error: No MCP handler provided for {item.path}"

            try:
                # Parse path: "server.tool" or "server.tool(args)"
                # But here path is already "gnosis" (server) if tool_chain is set?
                # Parser sets tool_chain="mcp:gnosis.tool('search')"

                target = item.tool_chain if item.tool_chain else item.path

                # Extract server, tool, args from target string
                # Expected format: "mcp:server.tool('args')" or "server.tool"

                # Clean up prefix
                if target.startswith("mcp:"):
                    target = target[4:]

                server_name = target.split(".")[0]

                # Check for .tool("args") pattern
                tool_match = re.search(r'\.tool\((["\']?)(.+?)\1\)', target)
                if tool_match:
                    tool_name = tool_match.group(2)
                    # We might need to parse args more complexly later
                    args = {} # Arguments usually passed via .with() or similar in Prompt-Lang v2 spec?
                    # The spec says: mcp:gnosis.tool("search")
                    # So tool name is passed as argument to .tool()?
                    # Or is it mcp:gnosis.search?

                    # Based on parser:
                    # if ref_type == "mcp" and ".tool(" in path:
                    #    tool_chain = path

                    # So we have "gnosis.tool('search')"
                    return await mcp_handler(server_name, tool_name, {})
                else:
                     return f"Error resolving MCP URI: {target}"

            except Exception as e:
                return f"MCP Error: {e}"

        return self._resolve_context_item(item)
    
    def _evaluate_condition(self, cond: 'Condition', context: dict) -> bool:
        """Evaluate a condition against the context."""
        var_value = context.get(cond.variable)
        if var_value is None:
            return False
        
        if cond.operator == "==":
            return str(var_value) == str(cond.value)
        elif cond.operator == "!=":
            return str(var_value) != str(cond.value)
        elif cond.operator == ">":
            return float(var_value) > float(cond.value)
        elif cond.operator == "<":
            return float(var_value) < float(cond.value)
        elif cond.operator == ">=":
            return float(var_value) >= float(cond.value)
        elif cond.operator == "<=":
            return float(var_value) <= float(cond.value)
        
        return False
    
    def _resolve_context_item(self, item: 'ContextItem') -> Optional[str]:
        """Resolve a context item to its content string."""
        import os
        import glob as glob_module
        
        if item.ref_type == "file":
            # Read actual file
            path = Path(item.path)
            if path.exists():
                try:
                    content = path.read_text(encoding='utf-8')
                    # Truncate if too long (based on priority)
                    max_lines = {"HIGH": 200, "MEDIUM": 100, "LOW": 50}.get(item.priority, 100)
                    lines = content.split('\n')
                    if len(lines) > max_lines:
                        content = '\n'.join(lines[:max_lines]) + f"\n... ({len(lines) - max_lines} more lines)"
                    return content
                except Exception as e:
                    return f"Error reading file: {e}"
            else:
                return f"File not found: {item.path}"
        
        elif item.ref_type == "dir":
            # List files in directory
            path = Path(item.path)
            if path.exists() and path.is_dir():
                try:
                    pattern = item.filter or "*"
                    max_depth = item.depth or 1
                    
                    # Use glob to find files
                    if max_depth == 1:
                        files = list(path.glob(pattern))
                    else:
                        files = list(path.glob(f"**/{pattern}"))
                    
                    # Limit results
                    files = files[:20]
                    return "\n".join(str(f.relative_to(path)) for f in files)
                except Exception as e:
                    return f"Error listing directory: {e}"
            else:
                return f"Directory not found: {item.path}"
        
        elif item.ref_type == "conv":
            # Placeholder for conversation reference
            return f"[Conversation: {item.path}]"
        
        elif item.ref_type == "mcp":
            # Placeholder for MCP server reference
            return f"[MCP Server: {item.path}]"
        
        elif item.ref_type == "ki":
            # Placeholder for Knowledge Item
            return f"[Knowledge Item: {item.path}]"
        
        return None


# v2.1 additions
@dataclass
class ParseResult:
    """Result of parsing a prompt-lang file with multiple definitions."""
    prompts: dict[str, Prompt] = field(default_factory=dict)  # name -> Prompt
    mixins: dict[str, Mixin] = field(default_factory=dict)    # name -> Mixin
    
    def get_prompt(self, name: str) -> Optional[Prompt]:
        """Get a prompt by name."""
        return self.prompts.get(name)
    
    def get_mixin(self, name: str) -> Optional[Mixin]:
        """Get a mixin by name."""
        return self.mixins.get(name)
    
    def get(self, name: str) -> Optional[Prompt | Mixin]:
        """Get a prompt or mixin by name."""
        return self.prompts.get(name) or self.mixins.get(name)


class ParseError(Exception):
    """Error during parsing."""
    def __init__(self, message: str, line: int = 0):
        self.line = line
        super().__init__(f"Line {line}: {message}" if line else message)


class PromptLangParser:
    """Parser for prompt-lang files."""
    
    # Regex patterns
    HEADER_PATTERN = re.compile(r'^#prompt\s+([a-z_][a-z0-9_-]*)$')
    MIXIN_HEADER_PATTERN = re.compile(r'^#mixin\s+([a-z_][a-z0-9_-]*)$')  # v2.1
    BLOCK_PATTERN = re.compile(r'^(@\w+):$')
    LIST_ITEM_PATTERN = re.compile(r'^  - (.+)$')
    TOOL_ITEM_PATTERN = re.compile(r'^  - ([a-z_][a-z0-9_-]*): (.+)$')
    EXAMPLE_INPUT_PATTERN = re.compile(r'^  - input: (.+)$')
    EXAMPLE_OUTPUT_PATTERN = re.compile(r'^  +output: (.+)$')  # Allow flexible indent
    FENCED_START_PATTERN = re.compile(r'^  ```(\w*)$')
    FENCED_END_PATTERN = re.compile(r'^  ```\s*$')  # Allow trailing whitespace
    INDENTED_LINE_PATTERN = re.compile(r'^  (.+)$')
    # v2.1 patterns for extends/mixin
    EXTENDS_INLINE_PATTERN = re.compile(r'^@extends:\s*(.+)$')
    MIXIN_REF_PATTERN = re.compile(r'^@mixin:\s*\[([^\]]+)\]$')
    
    def __init__(self, content: str):
        self.content = content
        self.lines = content.split('\n')
        self.pos = 0
        self.prompt: Optional[Prompt] = None
    
    def parse(self) -> Prompt:
        """Parse the content and return a Prompt object."""
        self._skip_empty_lines()
        self._parse_header()
        
        while self.pos < len(self.lines):
            self._skip_empty_lines()
            if self.pos >= len(self.lines):
                break
            self._parse_block()
        
        return self.prompt
    
    def _skip_empty_lines(self):
        """Skip empty lines and comments."""
        while self.pos < len(self.lines):
            line = self.lines[self.pos].rstrip()
            if line and not line.startswith('//'):
                break
            self.pos += 1
    
    def _current_line(self) -> str:
        """Get current line."""
        if self.pos < len(self.lines):
            return self.lines[self.pos].rstrip()
        return ""
    
    def _parse_header(self):
        """Parse #prompt header."""
        line = self._current_line()
        match = self.HEADER_PATTERN.match(line)
        if not match:
            raise ParseError(f"Expected '#prompt <name>', got: {line}", self.pos + 1)
        
        self.prompt = Prompt(name=match.group(1))
        self.pos += 1
    
    def _parse_block(self):
        """Parse a block (@role, @goal, etc.)."""
        line = self._current_line()
        
        # Special handling for @if (doesn't match standard pattern)
        if line.startswith("@if "):
            condition = self._parse_condition_block()
            if condition:
                self.prompt.conditions.append(condition)
            return
        
        # v2.1: Check for inline @extends: name
        extends_match = self.EXTENDS_INLINE_PATTERN.match(line)
        if extends_match:
            self.prompt.extends = extends_match.group(1).strip()
            self.pos += 1
            return
        
        # v2.1: Check for inline @mixin: [name1, name2]
        mixin_match = self.MIXIN_REF_PATTERN.match(line)
        if mixin_match:
            mixins_str = mixin_match.group(1)
            self.prompt.mixins = [m.strip() for m in mixins_str.split(',')]
            self.pos += 1
            return
        
        match = self.BLOCK_PATTERN.match(line)
        if not match:
            # Skip unknown lines
            self.pos += 1
            return
        
        block_type = match.group(1)
        self.pos += 1
        
        if block_type == "@role":
            self.prompt.role = self._parse_text_content()
        elif block_type == "@goal":
            self.prompt.goal = self._parse_text_content()
        elif block_type == "@constraints":
            self.prompt.constraints = self._parse_list_content()
        elif block_type == "@format":
            self.prompt.format = self._parse_format_content()
        elif block_type == "@examples":
            self.prompt.examples = self._parse_example_content()
        elif block_type == "@tools":
            self.prompt.tools = self._parse_tool_content()
        elif block_type == "@resources":
            self.prompt.resources = self._parse_tool_content()  # Same format
        # v2 additions
        elif block_type == "@rubric":
            self.prompt.rubric = self._parse_rubric_content()
        elif block_type == "@activation":
            self.prompt.activation = self._parse_activation_content()
        elif block_type == "@if":
            # Re-parse with condition
            self.pos -= 1  # Go back to @if line
            condition = self._parse_condition_block()
            if condition:
                self.prompt.conditions.append(condition)
        # v2.0.1 additions
        elif block_type == "@context":
            self.prompt.context = self._parse_context_content()

    
    def _parse_text_content(self) -> str:
        """Parse indented text content."""
        lines = []
        while self.pos < len(self.lines):
            line = self._current_line()
            match = self.INDENTED_LINE_PATTERN.match(line)
            if match:
                lines.append(match.group(1))
                self.pos += 1
            elif line == "" or line.startswith('@') or line.startswith('#'):
                break
            else:
                self.pos += 1
                break
        return "\n".join(lines)
    
    def _parse_list_content(self) -> list[str]:
        """Parse list items."""
        items = []
        while self.pos < len(self.lines):
            line = self._current_line()
            match = self.LIST_ITEM_PATTERN.match(line)
            if match:
                items.append(match.group(1))
                self.pos += 1
            elif line == "":
                self.pos += 1
            elif line.startswith('@') or line.startswith('#'):
                break
            else:
                break
        return items
    
    def _parse_format_content(self) -> str:
        """Parse format content (may include fenced code block)."""
        lines = []
        in_fenced = False
        
        while self.pos < len(self.lines):
            line = self.lines[self.pos].rstrip()  # Use raw line, stripped
            
            # Check for fenced block start (only if not already in fenced)
            if not in_fenced and line.startswith("  ```"):
                in_fenced = True
                lines.append(line[2:])  # Remove 2-space indent
                self.pos += 1
                continue
            
            # Check for fenced block end
            if in_fenced:
                if line.strip() == "```" or line == "  ```":
                    lines.append("```")
                    self.pos += 1
                    break  # Exit after fenced block ends
                else:
                    # Inside fenced block, keep content
                    if line.startswith("  "):
                        lines.append(line[2:])
                    else:
                        lines.append(line)
                    self.pos += 1
                    continue
            
            # Regular indented content (not in fenced block)
            if line.startswith("  ") and not line.startswith("  -"):
                lines.append(line[2:])
                self.pos += 1
            elif line == "":
                self.pos += 1
            elif line.startswith('@') or line.startswith('#'):
                break
            else:
                break
        
        return "\n".join(lines)
    
    def _parse_example_content(self) -> list[dict]:
        """Parse example items."""
        examples = []
        current = {}
        
        while self.pos < len(self.lines):
            line = self._current_line()
            
            input_match = self.EXAMPLE_INPUT_PATTERN.match(line)
            output_match = self.EXAMPLE_OUTPUT_PATTERN.match(line)
            
            if input_match:
                if current:
                    examples.append(current)
                current = {"input": input_match.group(1)}
                self.pos += 1
            elif output_match:
                current["output"] = output_match.group(1)
                self.pos += 1
            elif line == "":
                self.pos += 1
            elif line.startswith('@') or line.startswith('#'):
                break
            else:
                break
        
        if current:
            examples.append(current)
        
        return examples
    
    def _parse_tool_content(self) -> dict[str, str]:
        """Parse tool/resource items."""
        items = {}
        while self.pos < len(self.lines):
            line = self._current_line()
            match = self.TOOL_ITEM_PATTERN.match(line)
            if match:
                items[match.group(1)] = match.group(2)
                self.pos += 1
            elif line == "":
                self.pos += 1
            elif line.startswith('@') or line.startswith('#'):
                break
            else:
                break
        return items

    def _parse_context_content(self) -> list[ContextItem]:
        """Parse @context block content."""
        items = []
        
        while self.pos < len(self.lines):
            line = self._current_line()
            
            # Check for context item: "  - type:"path" [options]"
            # Patterns: file:"path", dir:"path", conv:"title", mcp:server, ki:"name"
            item_match = re.match(r'^  - (file|dir|conv|mcp|ki):(["\']?)([^"\']+)\2(.*)$', line)
            if item_match:
                ref_type = item_match.group(1)
                path = item_match.group(3)
                options_str = item_match.group(4).strip()
                
                # Parse options [priority=HIGH, section="..."]
                priority = "MEDIUM"
                section = None
                filter_opt = None
                depth = None
                tool_chain = None
                
                if options_str:
                    # Parse filter options (filter="*.ts", depth=2)
                    filter_match = re.search(r'\(filter=["\']?([^"\']+)["\']?', options_str)
                    if filter_match:
                        filter_opt = filter_match.group(1)
                    depth_match = re.search(r'depth=(\d+)', options_str)
                    if depth_match:
                        depth = int(depth_match.group(1))
                    
                    # Parse bracket options [priority=HIGH]
                    if "[" in options_str:
                        bracket_content = re.search(r'\[([^\]]+)\]', options_str)
                        if bracket_content:
                            opts = bracket_content.group(1)
                            priority_match = re.search(r'priority=(HIGH|MEDIUM|LOW)', opts)
                            if priority_match:
                                priority = priority_match.group(1)
                            section_match = re.search(r'section=["\']?([^"\']+)["\']?', opts)
                            if section_match:
                                section = section_match.group(1)
                    
                    # Parse MCP tool chain
                    if ref_type == "mcp" and ".tool(" in path:
                        tool_chain = path
                        path = path.split(".")[0]
                
                items.append(ContextItem(
                    ref_type=ref_type,
                    path=path,
                    priority=priority,
                    section=section,
                    filter=filter_opt,
                    depth=depth,
                    tool_chain=tool_chain
                ))
                self.pos += 1
            elif line == "":
                self.pos += 1
            elif line.startswith('@') or line.startswith('#'):
                break
            else:
                break
        
        return items

    def _parse_rubric_content(self) -> Rubric:
        """Parse @rubric block content."""
        rubric = Rubric()
        current_dimension = None
        
        while self.pos < len(self.lines):
            line = self._current_line()
            
            # Check for dimension header: "  - dimension_name:"
            dim_match = re.match(r'^  - ([a-z_][a-z0-9_-]*):$', line)
            if dim_match:
                if current_dimension:
                    rubric.dimensions.append(current_dimension)
                current_dimension = RubricDimension(
                    name=dim_match.group(1),
                    description="",
                    scale="1-5"
                )
                self.pos += 1
                continue
            
            # Check for dimension properties (6-space indent)
            if current_dimension and line.startswith("      "):
                prop_line = line.strip()
                if prop_line.startswith("description:"):
                    current_dimension.description = prop_line[12:].strip().strip('"\'')
                elif prop_line.startswith("scale:"):
                    current_dimension.scale = prop_line[6:].strip()
                elif prop_line.startswith("criteria:"):
                    # Parse criteria block
                    self.pos += 1
                    while self.pos < len(self.lines):
                        crit_line = self._current_line()
                        crit_match = re.match(r'^        (\d+): (.+)$', crit_line)
                        if crit_match:
                            current_dimension.criteria[crit_match.group(1)] = crit_match.group(2).strip('"\'')
                            self.pos += 1
                        elif crit_line.startswith("        "):
                            self.pos += 1
                        else:
                            break
                    continue
                self.pos += 1
                continue
            
            # Check for output spec: "  output:"
            if line == "  output:":
                self.pos += 1
                while self.pos < len(self.lines):
                    out_line = self._current_line()
                    if out_line.startswith("    format:"):
                        rubric.output_format = out_line[11:].strip().strip('"\'')
                    elif out_line.startswith("    key:"):
                        rubric.output_key = out_line[8:].strip().strip('"\'')
                    elif out_line.startswith("    "):
                        pass
                    else:
                        break
                    self.pos += 1
                continue
            
            # End conditions
            if line == "":
                self.pos += 1
            elif line.startswith('@') or line.startswith('#'):
                break
            else:
                break
        
        if current_dimension:
            rubric.dimensions.append(current_dimension)
        
        return rubric

    def _parse_activation_content(self) -> Activation:
        """Parse @activation block content."""
        activation = Activation()
        
        while self.pos < len(self.lines):
            line = self._current_line()
            
            # Parse key: value pairs with 2-space indent
            if line.startswith("  ") and ":" in line:
                stripped = line[2:].strip()
                if stripped.startswith("mode:"):
                    activation.mode = stripped[5:].strip().strip('"\'')
                elif stripped.startswith("pattern:"):
                    activation.pattern = stripped[8:].strip().strip('"\'')
                elif stripped.startswith("priority:"):
                    try:
                        activation.priority = int(stripped[9:].strip())
                    except ValueError:
                        activation.priority = 1
                elif stripped.startswith("rules:"):
                    # Parse rules list: [rule1, rule2]
                    rules_str = stripped[6:].strip()
                    if rules_str.startswith("[") and rules_str.endswith("]"):
                        rules_str = rules_str[1:-1]
                        activation.rules = [r.strip().strip('"\'') for r in rules_str.split(",") if r.strip()]
                self.pos += 1
            elif line == "":
                self.pos += 1
            elif line.startswith('@') or line.startswith('#'):
                break
            else:
                break
        
        return activation

    def _parse_condition_block(self) -> Optional[Condition]:
        """Parse @if/@else/@endif block."""
        line = self._current_line()
        
        # Parse @if condition:
        if_match = re.match(r'^@if\s+(\w+)\s*(==|!=|>|<|>=|<=)\s*["\']?([^"\']+)["\']?\s*:$', line)
        if not if_match:
            self.pos += 1
            return None
        
        condition = Condition(
            variable=if_match.group(1),
            operator=if_match.group(2),
            value=if_match.group(3)
        )
        self.pos += 1
        
        # Collect if_content until @else or @endif
        if_lines = []
        while self.pos < len(self.lines):
            line = self._current_line()
            if line == "@else:":
                self.pos += 1
                break
            elif line == "@endif":
                self.pos += 1
                return condition
            elif line.startswith("  "):
                if_lines.append(line[2:])
                self.pos += 1
            elif line == "":
                self.pos += 1
            else:
                break
        
        condition.if_content = {"raw": "\n".join(if_lines)}
        
        # Collect else_content until @endif
        else_lines = []
        while self.pos < len(self.lines):
            line = self._current_line()
            if line == "@endif":
                self.pos += 1
                break
            elif line.startswith("  "):
                else_lines.append(line[2:])
                self.pos += 1
            elif line == "":
                self.pos += 1
            else:
                break
        
        condition.else_content = {"raw": "\n".join(else_lines)}
        
        return condition


def parse_file(filepath: str) -> Prompt:
    """Parse a .prompt file."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    content = path.read_text(encoding='utf-8')
    parser = PromptLangParser(content)
    return parser.parse()


# v2.1 additions: parse_all and resolve functions
def parse_all(content: str) -> ParseResult:
    """
    Parse content with multiple prompts and mixins.
    
    Supports:
        #prompt name
        #mixin name
    
    Returns:
        ParseResult with all prompts and mixins
    """
    result = ParseResult()
    lines = content.split('\n')
    pos = 0
    
    while pos < len(lines):
        line = lines[pos].rstrip()
        
        # Skip empty lines and comments
        if not line or line.startswith('//'):
            pos += 1
            continue
        
        # Check for #mixin header
        mixin_match = PromptLangParser.MIXIN_HEADER_PATTERN.match(line)
        if mixin_match:
            name = mixin_match.group(1)
            # Extract mixin content until next # header
            mixin_lines = [line]
            pos += 1
            while pos < len(lines):
                next_line = lines[pos].rstrip()
                if next_line.startswith('#prompt') or next_line.startswith('#mixin'):
                    break
                mixin_lines.append(next_line)
                pos += 1
            
            # Parse as prompt and convert to Mixin
            mixin_content = '\n'.join(mixin_lines).replace('#mixin', '#prompt', 1)
            parser = PromptLangParser(mixin_content)
            prompt = parser.parse()
            mixin = Mixin(
                name=name,
                role=prompt.role,
                goal=prompt.goal,
                constraints=prompt.constraints,
                format=prompt.format,
                examples=prompt.examples,
                tools=prompt.tools,
                resources=prompt.resources,
                rubric=prompt.rubric,
                activation=prompt.activation,
                context=prompt.context
            )
            result.mixins[name] = mixin
            continue
        
        # Check for #prompt header
        prompt_match = PromptLangParser.HEADER_PATTERN.match(line)
        if prompt_match:
            name = prompt_match.group(1)
            # Extract prompt content until next # header
            prompt_lines = [line]
            pos += 1
            while pos < len(lines):
                next_line = lines[pos].rstrip()
                if next_line.startswith('#prompt') or next_line.startswith('#mixin'):
                    break
                prompt_lines.append(next_line)
                pos += 1
            
            prompt_content = '\n'.join(prompt_lines)
            parser = PromptLangParser(prompt_content)
            prompt = parser.parse()
            result.prompts[name] = prompt
            continue
        
        pos += 1
    
    return result


def _merge(parent: Prompt | Mixin, child: Prompt) -> Prompt:
    """
    Merge parent into child. Child takes precedence for scalar fields.
    
    Rules:
        - str fields (role, goal, format): child overrides
        - list fields (constraints, examples, context): concatenate (parent + child)
        - dict fields (tools, resources): merge (child overrides)
        - complex fields (rubric, activation): child overrides
    """
    return Prompt(
        name=child.name,
        role=child.role or parent.role,
        goal=child.goal or parent.goal,
        constraints=parent.constraints + child.constraints,  # concatenate
        format=child.format or parent.format,
        examples=parent.examples + child.examples,  # concatenate
        tools={**parent.tools, **child.tools},  # child overrides
        resources={**parent.resources, **child.resources},
        rubric=child.rubric or parent.rubric,
        conditions=parent.conditions + child.conditions if hasattr(parent, 'conditions') and parent.conditions else child.conditions,
        activation=child.activation or parent.activation,
        context=parent.context + child.context,  # concatenate
        extends=None,  # resolved
        mixins=[],     # resolved
        _resolved=True
    )


def resolve(prompt: Prompt, registry: ParseResult) -> Prompt:
    """
    Resolve extends and mixins for a prompt.
    
    Resolution order:
        1. Mixins (left to right)
        2. Extends (recursive, depth-first)
        3. Self
    
    Args:
        prompt: The prompt to resolve
        registry: ParseResult containing all prompts and mixins
    
    Returns:
        Resolved Prompt with _resolved=True
    
    Raises:
        CircularReferenceError: If circular reference is detected
        ReferenceError: If referenced prompt/mixin is not found
    """
    if prompt._resolved:
        return prompt
    
    visited: set[str] = {prompt.name}
    chain: list[str] = [prompt.name]
    
    return _resolve_with_chain(prompt, registry, visited, chain)


def _resolve_with_chain(
    prompt: Prompt,
    registry: ParseResult,
    visited: set[str],
    chain: list[str]
) -> Prompt:
    """Internal resolver with cycle detection."""
    result = prompt
    
    # 1. Apply mixins (left to right)
    for mixin_name in prompt.mixins:
        mixin = registry.get_mixin(mixin_name)
        if not mixin:
            raise ReferenceError(mixin_name)
        result = _merge(mixin, result)
    
    # 2. Apply extends (recursive)
    if prompt.extends:
        parent_name = prompt.extends
        
        if parent_name in visited:
            raise CircularReferenceError(chain + [parent_name])
        
        parent = registry.get_prompt(parent_name) or registry.get_mixin(parent_name)
        if not parent:
            raise ReferenceError(parent_name)
        
        visited.add(parent_name)
        chain.append(parent_name)
        
        # Recursively resolve parent if it's a Prompt
        if isinstance(parent, Prompt) and (parent.extends or parent.mixins):
            parent = _resolve_with_chain(parent, registry, visited, chain)
        
        result = _merge(parent, result)
    
    result._resolved = True
    return result


def validate_file(filepath: str) -> tuple[bool, str]:
    """Validate a .prompt file."""
    try:
        prompt = parse_file(filepath)
        
        # Check required fields
        errors = []
        if not prompt.role:
            errors.append("Missing required block: @role")
        if not prompt.goal:
            errors.append("Missing required block: @goal")
        
        if errors:
            return False, "\n".join(errors)
        return True, "Valid"
    except ParseError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error: {e}"


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    filepath = sys.argv[2]
    
    if command == "parse":
        try:
            prompt = parse_file(filepath)
            print(prompt.to_json())
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif command == "validate":
        valid, message = validate_file(filepath)
        print(message)
        sys.exit(0 if valid else 1)
    
    elif command == "expand":
        try:
            prompt = parse_file(filepath)
            print(prompt.expand())
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    elif command == "compile":
        try:
            prompt = parse_file(filepath)
            # Parse context from --context "key=value,key2=value2"
            context = {}
            for arg in sys.argv[3:]:
                if arg.startswith("--context="):
                    pairs = arg[10:].split(",")
                    for pair in pairs:
                        if "=" in pair:
                            k, v = pair.split("=", 1)
                            context[k.strip()] = v.strip()
            print(prompt.compile(context=context))
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
