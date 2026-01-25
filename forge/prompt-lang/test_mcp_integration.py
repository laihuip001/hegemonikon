#!/usr/bin/env python3
"""
MCP Integration Tests for Prompt-Lang
=====================================
"""

import sys
import unittest
import time
import os
from pathlib import Path
import json

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    from prompt_lang import PromptLangParser, Prompt, ContextItem
except ImportError:
    # Try importing assuming we are in forge/prompt-lang
    import prompt_lang
    PromptLangParser = prompt_lang.PromptLangParser
    Prompt = prompt_lang.Prompt
    ContextItem = prompt_lang.ContextItem

class TestMCPContextResolution(unittest.TestCase):

    def setUp(self):
        # Ensure we are in the right place relative to repo
        self.root = Path(__file__).resolve().parent.parent.parent
        self.mcp_server_script = self.root / "mcp" / "prompt_lang_server.py"

        if not self.mcp_server_script.exists():
            self.skipTest(f"MCP server script not found at {self.mcp_server_script}")

    def test_resolve_mcp_generate(self):
        """Test resolving mcp:prompt-lang-generator.tool("generate")"""

        # We need to escape quotes in JSON for the context line
        # requirements: "create a math tutor skill"

        content = """#prompt test-mcp-gen

@role:
  Tester

@goal:
  Test MCP resolution

@context:
  - mcp:prompt-lang-generator.tool("generate", {"requirements": "create a math tutor skill"})
"""
        parser = PromptLangParser(content)
        prompt = parser.parse()

        self.assertEqual(len(prompt.context), 1)
        item = prompt.context[0]
        self.assertEqual(item.ref_type, "mcp")

        # Compile should trigger resolution
        print("Compiling prompt with MCP context...")
        compiled = prompt.compile()
        print("Compilation Result snippet:", compiled[:200])

        # Check if output contains generated content
        # The prompt_lang_server returns a stub with "// Generated from requirements: create a math tutor skill"

        self.assertIn("// Generated from requirements: create a math tutor skill", compiled)
        # Should contain the template content too (if template exists or fallback)
        # base_template.yaml doesn't have #prompt, but usually has version info or comments
        self.assertIn("Prompt-Lang v2.0 Base Template", compiled)

    def test_resolve_mcp_validate(self):
        """Test resolving mcp:prompt-lang-generator.tool("validate")"""

        # We pass code to validate
        # We need to construct a JSON string that is valid JSON when parsed by prompt_lang
        # The regex extracts the part after comma.

        # Code: #prompt valid-test\n@role: r\n@goal: g
        # Use real newlines so json.dumps escapes them as \n, which prompt_lang parser reads as one line
        # Note: prompt-lang requires indentation for content
        code_val = "#prompt valid-test\n@role:\n  r\n@goal:\n  g"
        args_dict = {"code": code_val}
        args_json = json.dumps(args_dict)

        # In the file content, this JSON string is placed literally.
        # But wait, prompt_lang parser reads lines.
        # If I put single quotes around arguments?

        content = f"""#prompt test-mcp-val

@role:
  Tester

@goal:
  Test MCP resolution

@context:
  - mcp:prompt-lang-generator.tool("validate", {args_json})
"""
        parser = PromptLangParser(content)
        prompt = parser.parse()

        compiled = prompt.compile()

        # Should contain "Valid"
        self.assertIn("Valid", compiled)

if __name__ == "__main__":
    unittest.main(verbosity=2)
