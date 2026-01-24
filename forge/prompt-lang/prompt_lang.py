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
        
        return "\n".join(parts)


class ParseError(Exception):
    """Error during parsing."""
    def __init__(self, message: str, line: int = 0):
        self.line = line
        super().__init__(f"Line {line}: {message}" if line else message)


class PromptLangParser:
    """Parser for prompt-lang files."""
    
    # Regex patterns
    HEADER_PATTERN = re.compile(r'^#prompt\s+([a-z_][a-z0-9_-]*)$')
    BLOCK_PATTERN = re.compile(r'^(@\w+):$')
    LIST_ITEM_PATTERN = re.compile(r'^  - (.+)$')
    TOOL_ITEM_PATTERN = re.compile(r'^  - ([a-z_][a-z0-9_-]*): (.+)$')
    EXAMPLE_INPUT_PATTERN = re.compile(r'^  - input: (.+)$')
    EXAMPLE_OUTPUT_PATTERN = re.compile(r'^  +output: (.+)$')  # Allow flexible indent
    FENCED_START_PATTERN = re.compile(r'^  ```(\w*)$')
    FENCED_END_PATTERN = re.compile(r'^  ```\s*$')  # Allow trailing whitespace
    INDENTED_LINE_PATTERN = re.compile(r'^  (.+)$')
    
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
    
    else:
        print(f"Unknown command: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
