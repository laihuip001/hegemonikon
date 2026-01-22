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
