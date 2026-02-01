# PROOF: [L2/インフラ] S2→プロンプト言語が必要→test_prompt_lang が担う
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

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from prompt_lang import Prompt, PromptLangParser, ParseError, parse_file, validate_file


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
            constraints=["Test constraint"],
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


class TestExtendsAndMixin(unittest.TestCase):
    """Test cases for v2.1 @extends and @mixin features."""

    def test_basic_extends(self):
        """Test basic template inheritance."""
        from prompt_lang import parse_all, resolve

        content = """#prompt base_spec
@role:
  Base role

@goal:
  Base goal

@constraints:
  - Base constraint

#prompt child_spec
@extends: base_spec
@goal:
  Child goal

@constraints:
  - Child constraint
"""
        result = parse_all(content)
        child = result.get_prompt("child_spec")
        resolved = resolve(child, result)

        self.assertEqual(resolved.role, "Base role")  # inherited
        self.assertEqual(resolved.goal, "Child goal")  # overridden
        self.assertEqual(len(resolved.constraints), 2)  # concatenated
        self.assertIn("Base constraint", resolved.constraints)
        self.assertIn("Child constraint", resolved.constraints)

    def test_mixin_composition(self):
        """Test mixin composition."""
        from prompt_lang import parse_all, resolve

        content = """#mixin json_output
@format:
  type: json

@constraints:
  - Output must be valid JSON

#prompt my_prompt
@mixin: [json_output]
@role:
  JSON generator
@goal:
  Generate JSON
"""
        result = parse_all(content)
        prompt = result.get_prompt("my_prompt")
        resolved = resolve(prompt, result)

        self.assertEqual(resolved.role, "JSON generator")
        self.assertIn("type: json", resolved.format)
        self.assertIn("Output must be valid JSON", resolved.constraints)

    def test_multiple_mixins(self):
        """Test multiple mixin composition (left to right)."""
        from prompt_lang import parse_all, resolve

        content = """#mixin mixin_a
@constraints:
  - Constraint A

#mixin mixin_b
@constraints:
  - Constraint B

#prompt multi_mixin
@mixin: [mixin_a, mixin_b]
@role:
  Multi mixin role
@goal:
  Test
@constraints:
  - Constraint C
"""
        result = parse_all(content)
        prompt = result.get_prompt("multi_mixin")
        resolved = resolve(prompt, result)

        # Should have constraints from both mixins + self
        self.assertEqual(len(resolved.constraints), 3)

    def test_extends_with_mixin(self):
        """Test extends combined with mixin."""
        from prompt_lang import parse_all, resolve

        content = """#mixin common_format
@format:
  markdown

#prompt parent
@role:
  Parent role
@goal:
  Parent goal

#prompt child
@extends: parent
@mixin: [common_format]
@constraints:
  - Child constraint
"""
        result = parse_all(content)
        child = result.get_prompt("child")
        resolved = resolve(child, result)

        self.assertEqual(resolved.role, "Parent role")
        self.assertEqual(resolved.goal, "Parent goal")
        self.assertIn("markdown", resolved.format)

    def test_circular_reference_detection(self):
        """Test that circular references raise error."""
        from prompt_lang import parse_all, resolve, CircularReferenceError

        content = """#prompt a
@extends: b
@role:
  A
@goal:
  A

#prompt b
@extends: a
@role:
  B
@goal:
  B
"""
        result = parse_all(content)
        prompt_a = result.get_prompt("a")

        with self.assertRaises(CircularReferenceError):
            resolve(prompt_a, result)

    def test_undefined_reference(self):
        """Test that undefined references raise error."""
        from prompt_lang import (
            parse_all,
            resolve,
            ReferenceError as PromptReferenceError,
        )

        content = """#prompt child
@extends: nonexistent
@role:
  Child
@goal:
  Child
"""
        result = parse_all(content)
        child = result.get_prompt("child")

        with self.assertRaises(PromptReferenceError):
            resolve(child, result)

    def test_parse_all_multiple_prompts(self):
        """Test parsing multiple prompts in one file."""
        from prompt_lang import parse_all

        content = """#prompt first
@role:
  First role
@goal:
  First goal

#prompt second
@role:
  Second role
@goal:
  Second goal
"""
        result = parse_all(content)

        self.assertEqual(len(result.prompts), 2)
        self.assertIn("first", result.prompts)
        self.assertIn("second", result.prompts)

    def test_dict_merge_child_priority(self):
        """Test that dict fields use child priority."""
        from prompt_lang import parse_all, resolve

        content = """#prompt parent
@role:
  Parent
@goal:
  Parent
@tools:
  - search: Parent search
  - read: Parent read

#prompt child
@extends: parent
@tools:
  - search: Child search overrides
"""
        result = parse_all(content)
        child = result.get_prompt("child")
        resolved = resolve(child, result)

        # Child's search should override parent's
        self.assertEqual(resolved.tools["search"], "Child search overrides")
        # Parent's read should be inherited
        self.assertEqual(resolved.tools["read"], "Parent read")

    def test_already_resolved_prompt(self):
        """Test that already resolved prompts are returned as-is."""
        from prompt_lang import parse_all, resolve

        content = """#prompt simple
@role:
  Simple
@goal:
  Simple
"""
        result = parse_all(content)
        prompt = result.get_prompt("simple")

        resolved1 = resolve(prompt, result)
        resolved2 = resolve(resolved1, result)  # Should return same object

        self.assertTrue(resolved2._resolved)


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)
