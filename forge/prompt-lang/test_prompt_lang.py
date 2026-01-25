#!/usr/bin/env python3
"""
prompt-lang Unit Tests
======================

Test suite for prompt-lang parser and integration.

Usage:
    python test_prompt_lang.py
"""

import sys
import unittest
from pathlib import Path
from io import StringIO
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from prompt_lang import Prompt, PromptLangParser, ParseError, parse_file, validate_file, ContextItem


class TestPromptLangParser(unittest.TestCase):
    """Test cases for PromptLangParser."""
    
    def test_minimal_prompt(self):
        """Test parsing a minimal prompt with only required fields."""
        content = """#prompt test-minimal

@role:
  Test role

@goal:
  input -> output
"""
        parser = PromptLangParser(content)
        prompt = parser.parse()
        
        self.assertEqual(prompt.name, "test-minimal")
        self.assertEqual(prompt.role, "Test role")
        self.assertEqual(prompt.goal, "input -> output")
    
    def test_full_prompt(self):
        """Test parsing a prompt with all fields."""
        content = """#prompt test-full

@role:
  Full test role

@goal:
  complex input -> structured output

@constraints:
  - Constraint one
  - Constraint two

@tools:
  - search_web: Search the web
  - read_file: Read files

@resources:
  - kb: file:///path/to/kb

@format:
  ```json
  {"key": "value"}
  ```

@examples:
  - input: "test input"
    output: "test output"
"""
        parser = PromptLangParser(content)
        prompt = parser.parse()
        
        self.assertEqual(prompt.name, "test-full")
        self.assertEqual(prompt.role, "Full test role")
        self.assertEqual(prompt.goal, "complex input -> structured output")
        self.assertEqual(len(prompt.constraints), 2)
        self.assertEqual(prompt.constraints[0], "Constraint one")
        self.assertEqual(len(prompt.tools), 2)
        self.assertIn("search_web", prompt.tools)
        self.assertEqual(len(prompt.resources), 1)
        self.assertIn("kb", prompt.resources)
        self.assertIn("json", prompt.format)
        self.assertEqual(len(prompt.examples), 1)
        self.assertEqual(prompt.examples[0]["input"], '"test input"')
    
    def test_missing_header(self):
        """Test that missing header raises error."""
        content = """@role:
  Test role
"""
        parser = PromptLangParser(content)
        with self.assertRaises(ParseError):
            parser.parse()
    
    def test_expand(self):
        """Test expanding prompt to natural language."""
        content = """#prompt test-expand

@role:
  Expert assistant

@goal:
  question -> answer
"""
        parser = PromptLangParser(content)
        prompt = parser.parse()
        expanded = prompt.expand()
        
        self.assertIn("You are Expert assistant", expanded)
        self.assertIn("Your task: question -> answer", expanded)
    
    def test_to_json(self):
        """Test JSON serialization."""
        content = """#prompt test-json

@role:
  JSON test

@goal:
  test -> pass
"""
        parser = PromptLangParser(content)
        prompt = parser.parse()
        json_str = prompt.to_json()
        
        self.assertIn('"name": "test-json"', json_str)
        self.assertIn('"role": "JSON test"', json_str)
    
    def test_empty_constraints(self):
        """Test parsing prompt with no constraints."""
        content = """#prompt test-no-constraints

@role:
  Simple role

@goal:
  in -> out
"""
        parser = PromptLangParser(content)
        prompt = parser.parse()
        
        self.assertEqual(prompt.constraints, [])
    
    def test_multiline_goal(self):
        """Test parsing multi-line goal."""
        content = """#prompt test-multiline

@role:
  Multiline test

@goal:
  complex input with
  multiple lines -> output
"""
        parser = PromptLangParser(content)
        prompt = parser.parse()
        
        self.assertIn("complex input with", prompt.goal)
        self.assertIn("multiple lines", prompt.goal)


class TestValidation(unittest.TestCase):
    """Test cases for validation."""
    
    def test_valid_file(self):
        """Test validating a valid prompt."""
        content = """#prompt valid

@role:
  Valid role

@goal:
  valid -> pass
"""
        # Create temp file
        temp_path = Path(__file__).parent / "staging" / "_test_valid.prompt"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path.write_text(content, encoding="utf-8")
        
        try:
            valid, msg = validate_file(str(temp_path))
            self.assertTrue(valid)
            self.assertEqual(msg, "Valid")
        finally:
            temp_path.unlink(missing_ok=True)
    
    def test_missing_role(self):
        """Test validation fails with missing role."""
        content = """#prompt missing-role

@goal:
  test -> fail
"""
        temp_path = Path(__file__).parent / "staging" / "_test_missing_role.prompt"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        temp_path.write_text(content, encoding="utf-8")
        
        try:
            valid, msg = validate_file(str(temp_path))
            self.assertFalse(valid)
            self.assertIn("@role", msg)
        finally:
            temp_path.unlink(missing_ok=True)


class TestIntegration(unittest.TestCase):
    """Integration tests for prompt_lang_integrate.py."""
    
    def test_generate_creates_file(self):
        """Test that generate creates a file in staging."""
        from prompt_lang_integrate import generate_prompt, STAGING_DIR
        
        filepath, prompt = generate_prompt(
            slug="_test-gen",
            role="Test role",
            goal="test -> pass",
            constraints=["Test constraint"]
        )
        
        try:
            self.assertTrue(filepath.exists())
            self.assertEqual(prompt.role, "Test role")
            self.assertEqual(len(prompt.constraints), 1)
        finally:
            filepath.unlink(missing_ok=True)
    
    def test_list_prompts(self):
        """Test listing prompts in staging."""
        from prompt_lang_integrate import list_prompts
        
        prompts = list_prompts()
        # Should return a list (may be empty or have items)
        self.assertIsInstance(prompts, list)


class TestMCPContext(unittest.TestCase):
    """Test cases for MCP Context resolution."""

    def test_parse_mcp_context(self):
        content = """#prompt test-mcp

@role:
  Test role

@goal:
  Test goal

@context:
  - mcp:gnosis.tool("search").with(query="AI agents")
  - mcp:other.tool("calc").with(a="1", b="2")
"""
        parser = PromptLangParser(content)
        prompt = parser.parse()

        self.assertEqual(len(prompt.context), 2)

        item1 = prompt.context[0]
        self.assertEqual(item1.ref_type, "mcp")
        self.assertEqual(item1.path, "gnosis")
        self.assertIn('.tool("search")', item1.tool_chain)
        self.assertIn('.with(query="AI agents")', item1.tool_chain)

    def test_compile_mcp_no_client(self):
        prompt = Prompt(name="test", role="R", goal="G")
        prompt.context.append(ContextItem(
            ref_type="mcp",
            path="gnosis",
            tool_chain='gnosis.tool("search").with(query="foo")'
        ))

        compiled = prompt.compile()
        self.assertIn("Runtime execution requires active MCP client", compiled)
        self.assertIn("gnosis:search(query=foo)", compiled)

    def test_compile_mcp_with_client_callable(self):
        prompt = Prompt(name="test", role="R", goal="G")
        prompt.context.append(ContextItem(
            ref_type="mcp",
            path="gnosis",
            tool_chain='gnosis.tool("search").with(query="foo")'
        ))

        mock_client = MagicMock(return_value="Search Results")

        compiled = prompt.compile(mcp_client=mock_client)

        self.assertIn("Search Results", compiled)
        mock_client.assert_called_with("gnosis", "search", {"query": "foo"})

    def test_compile_mcp_with_client_object(self):
        prompt = Prompt(name="test", role="R", goal="G")
        prompt.context.append(ContextItem(
            ref_type="mcp",
            path="gnosis",
            tool_chain='gnosis.tool("search").with(query="foo")'
        ))

        class MockClient:
            def call_tool(self, server, tool, args):
                return f"Called {server}:{tool} with {args}"

        compiled = prompt.compile(mcp_client=MockClient())

        self.assertIn("Called gnosis:search with {'query': 'foo'}", compiled)


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)
