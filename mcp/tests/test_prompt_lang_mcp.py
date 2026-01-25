import unittest
from pathlib import Path
import sys
import os

# Add mcp directory to path so we can import prompt_lang_mcp_server directly
sys.path.insert(0, str(Path(__file__).parent.parent))

from prompt_lang_mcp_server import PromptLangGenerator

class TestPromptLangGenerator(unittest.TestCase):
    def setUp(self):
        # Point to actual templates
        # We are in mcp/tests/, parent is mcp/, parent.parent is ROOT
        self.template_dir = Path(__file__).parent.parent.parent / ".agent/skills/utils/prompt-lang-generator/templates"
        if not self.template_dir.exists():
            self.skipTest(f"Template directory not found: {self.template_dir}")

        self.generator = PromptLangGenerator(self.template_dir)

    def test_detect_domain(self):
        self.assertEqual(self.generator.detect_domain("Write a python script to sort a list"), "technical")
        self.assertEqual(self.generator.detect_domain("Summarize this text"), "summarization")
        self.assertEqual(self.generator.detect_domain("Find papers about AI"), "academic")
        self.assertEqual(self.generator.detect_domain("Just a general request"), "general")

    def test_load_template(self):
        # Test loading technical template
        tmpl = self.generator.load_template("technical")
        self.assertIn("required", tmpl)

        # Check if domain specific constraints were merged
        constraints = tmpl["required"]["constraints"]
        found = False
        for c in constraints:
            if c and "OWASP" in c:
                found = True
                break
        self.assertTrue(found, "Technical constraints (OWASP) not found in merged template")

    def test_render_prompt(self):
        tmpl = self.generator.load_template("technical")
        output = self.generator.render_prompt(tmpl, "Create a secure login API", "technical")

        self.assertIn("#prompt technical_skill", output)
        self.assertIn("@role:", output)
        self.assertIn("@goal:", output)
        self.assertIn("Create a secure login API", output) # Check requirement injection
        self.assertIn("@rubric:", output) # Check if rubric is rendered

if __name__ == '__main__':
    unittest.main()
